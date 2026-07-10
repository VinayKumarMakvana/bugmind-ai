import ast
import os
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".py",
}


# =========================================================
# SAFE FILE READER
# =========================================================

def read_file(file_path: str) -> str:

    try:

        return Path(file_path).read_text(
            encoding="utf-8",
            errors="ignore",
        )

    except Exception:

        logger.exception(
            "Unable to read file: %s",
            file_path,
        )

        return ""


# =========================================================
# RAW CHUNK
# =========================================================

def build_raw_chunk(
    file_path: str,
    source: str,
) -> Dict[str, Any]:

    return {

        "content": source,

        "metadata": {

            "file": file_path,

            "type": "raw",

            "name": Path(file_path).name,

            "start_line": 1,

            "end_line": len(source.splitlines()),

        }

    }


# =========================================================
# NODE CHUNK
# =========================================================

def build_node_chunk(
    file_path: str,
    source_lines: List[str],
    node: ast.AST,
) -> Dict[str, Any]:

    start = node.lineno

    end = getattr(
        node,
        "end_lineno",
        start,
    )

    content = "\n".join(
        source_lines[start - 1:end]
    )

    return {

        "content": content,

        "metadata": {

            "file": file_path,

            "type": type(node).__name__,

            "name": getattr(
                node,
                "name",
                "",
            ),

            "start_line": start,

            "end_line": end,

        }

    }

# =========================================================
# PYTHON FILE CHUNKER
# =========================================================

def chunk_python_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a Python file and split it into
    functions, async functions and classes.
    """

    source = read_file(file_path)

    if not source:
        return []

    source_lines = source.splitlines()

    try:
        tree = ast.parse(source)

    except SyntaxError as ex:

        logger.warning(
            "Syntax Error in %s : %s",
            file_path,
            ex,
        )

        return [
            {
                **build_raw_chunk(
                    file_path,
                    source,
                ),
                "metadata": {
                    **build_raw_chunk(
                        file_path,
                        source,
                    )["metadata"],
                    "syntax_error": True,
                    "error": str(ex),
                },
            }
        ]

    chunks: List[Dict[str, Any]] = []

    imports = []

    for node in tree.body:

        if isinstance(node, ast.Import):

            for alias in node.names:

                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            imports.append(module)

    for node in ast.iter_child_nodes(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):

            chunk = build_node_chunk(
                file_path=file_path,
                source_lines=source_lines,
                node=node,
            )

            chunk["metadata"]["imports"] = imports

            chunk["metadata"]["docstring"] = ast.get_docstring(
                node
            )

            chunk["metadata"]["decorators"] = [

                ast.unparse(dec)

                if hasattr(ast, "unparse")

                else ""

                for dec in getattr(
                    node,
                    "decorator_list",
                    [],
                )

            ]

            if isinstance(node, ast.ClassDef):

                chunk["metadata"]["bases"] = [

                    ast.unparse(base)

                    if hasattr(ast, "unparse")

                    else ""

                    for base in node.bases

                ]

            chunks.append(chunk)

    if not chunks:

        chunks.append(
            build_raw_chunk(
                file_path,
                source,
            )
        )

    return chunks

# =========================================================
# REPOSITORY CHUNKER
# =========================================================

IGNORE_DIRECTORIES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "target",
    ".mypy_cache",
    ".pytest_cache",
}


def should_skip_directory(directory: str) -> bool:
    """
    Check whether directory should be skipped.
    """

    name = Path(directory).name

    if name.startswith("."):
        return True

    return name in IGNORE_DIRECTORIES


# =========================================================
# CHUNK REPOSITORY
# =========================================================

def chunk_repository(
    repo_path: str,
) -> List[Dict[str, Any]]:
    """
    Walk repository and create AST chunks.
    """

    repo = Path(repo_path)

    if not repo.exists():
        raise FileNotFoundError(
            f"Repository not found: {repo_path}"
        )

    all_chunks: List[Dict[str, Any]] = []

    visited = set()

    logger.info("Scanning repository...")

    for root, dirs, files in os.walk(repo):

        dirs[:] = [
            d
            for d in dirs
            if not should_skip_directory(d)
        ]

        for file in files:

            extension = Path(file).suffix.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                continue

            file_path = str(
                Path(root) / file
            )

            if file_path in visited:
                continue

            visited.add(file_path)

            try:

                chunks = chunk_python_file(
                    file_path
                )

                all_chunks.extend(chunks)

            except Exception:

                logger.exception(
                    "Failed parsing %s",
                    file_path,
                )

    logger.info(
        "Repository scan completed. %s chunks generated.",
        len(all_chunks),
    )

    return all_chunks


# =========================================================
# CHUNK STATISTICS
# =========================================================

def get_chunk_statistics(
    chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate repository chunk statistics.
    """

    stats = {
        "total_chunks": len(chunks),
        "functions": 0,
        "async_functions": 0,
        "classes": 0,
        "raw": 0,
    }

    for chunk in chunks:

        chunk_type = chunk.get(
            "metadata",
            {},
        ).get(
            "type",
            "raw",
        )

        if chunk_type == "FunctionDef":
            stats["functions"] += 1

        elif chunk_type == "AsyncFunctionDef":
            stats["async_functions"] += 1

        elif chunk_type == "ClassDef":
            stats["classes"] += 1

        else:
            stats["raw"] += 1

    return stats


# =========================================================
# SEARCH CHUNKS
# =========================================================

def search_chunks(
    chunks: List[Dict[str, Any]],
    keyword: str,
) -> List[Dict[str, Any]]:
    """
    Search keyword inside chunks.
    """

    keyword = keyword.lower()

    return [

        chunk

        for chunk in chunks

        if keyword in chunk["content"].lower()

    ]


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "chunk_python_file",

    "chunk_repository",

    "get_chunk_statistics",

    "search_chunks",

]