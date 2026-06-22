import ast
import os

def chunk_python_file(file_path):
    """Parse a python file and chunk it by functions/classes."""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
        
    try:
        tree = ast.parse(source)
    except Exception:
        return [{"content": source, "metadata": {"file": file_path, "type": "raw"}}]
        
    chunks = []
    lines = source.split('\n')
    
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1
            end_line = node.end_lineno
            chunk_content = '\n'.join(lines[start_line:end_line])
            chunks.append({
                "content": chunk_content,
                "metadata": {
                    "file": file_path,
                    "type": type(node).__name__,
                    "name": node.name
                }
            })
            
    if not chunks:
        chunks.append({"content": source, "metadata": {"file": file_path, "type": "raw"}})
        
    return chunks

def chunk_repository(repo_path):
    """Walk the repository and chunk supported files."""
    all_chunks = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                all_chunks.extend(chunk_python_file(file_path))
    return all_chunks
