from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...api.deps import get_current_user
from ...models.domain import User

logger = logging.getLogger(__name__)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# SCHEMAS
# =========================================================

class ExecuteRequest(BaseModel):
    code_content: str
    language: str


# =========================================================
# CONFIGURATION
# =========================================================

# Mapping of language id to its file extension and execution logic
# execution logic can be a single command [executable, file] or a custom function
LANGUAGE_CONFIG: Dict[str, Dict[str, Any]] = {
    "python": {"ext": ".py", "cmd": ["python" if shutil.which("python") else "python3"]},
    "javascript": {"ext": ".js", "cmd": ["node"]},
    "typescript": {"ext": ".ts", "cmd": ["ts-node"]},
    "php": {"ext": ".php", "cmd": ["php"]},
    "ruby": {"ext": ".rb", "cmd": ["ruby"]},
    "go": {"ext": ".go", "cmd": ["go", "run"]},
    "java": {"ext": ".java", "cmd": ["java"]},
    "rust": {"ext": ".rs", "compile": ["rustc", "{src}", "-o", "{exe}"], "run": ["{exe}"]},
    "cpp": {"ext": ".cpp", "compile": ["g++", "{src}", "-o", "{exe}"], "run": ["{exe}"]},
    "c": {"ext": ".c", "compile": ["gcc", "{src}", "-o", "{exe}"], "run": ["{exe}"]},
    "csharp": {"ext": ".cs", "cmd": ["csc", "{src}", "-out:{exe}"], "run": ["{exe}"]}, # Simplistic for Windows
    "shell": {"ext": ".sh", "cmd": ["bash"]},
}

NON_EXECUTABLE = ["json", "yaml", "markdown", "html", "css", "sql"]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_executable_from_config(config: Dict[str, Any]) -> Optional[str]:
    """
    Extract the main executable name from a language configuration.
    """
    if "cmd" in config:
        return config["cmd"][0]
    elif "compile" in config:
        return config["compile"][0]
    return None


def execute_in_temp_dir(config: Dict[str, Any], temp_dir: str, code_content: str) -> Dict[str, str]:
    """
    Compile and run the code inside a temporary directory.
    """
    src_path = os.path.join(temp_dir, f"main{config['ext']}")
    exe_path = os.path.join(temp_dir, "main.exe" if os.name == 'nt' else "main")
    
    with open(src_path, "w", encoding="utf-8") as f:
        f.write(code_content)
        
    try:
        # Compilation step (if needed)
        if "compile" in config:
            compile_cmd = [part.format(src=src_path, exe=exe_path) for part in config["compile"]]
            
            comp_process = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if comp_process.returncode != 0:
                logger.error("Compilation failed: %s", comp_process.stderr)
                return {
                    "status": "error",
                    "output": comp_process.stderr or comp_process.stdout
                }
            
            run_cmd = [part.format(exe=exe_path) for part in config["run"]]
        else:
            run_cmd = config["cmd"] + [src_path]
            
        # Execution step
        process = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        output = process.stdout
        if process.stderr:
            output += "\n" + process.stderr
            
        status_val = "success" if process.returncode == 0 else "error"
        
        return {
            "status": status_val,
            "output": output or "Program executed successfully but returned no output."
        }
        
    except subprocess.TimeoutExpired:
        logger.warning("Code execution timed out.")
        return {
            "status": "error",
            "output": "Execution timed out (5 seconds limit exceeded)."
        }
    except Exception as e:
        logger.exception("Unexpected error during execution")
        return {
            "status": "error",
            "output": f"An unexpected error occurred during execution: {str(e)}"
        }


# =========================================================
# ROUTES
# =========================================================

@router.post("")
@router.post("/")
async def execute_code(
    request: ExecuteRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Execute a code snippet in a sandboxed environment.
    """
    lang = request.language.lower()
    
    if lang in NON_EXECUTABLE:
        return {
            "status": "error",
            "output": f"Language '{lang}' cannot be executed directly."
        }
        
    config = LANGUAGE_CONFIG.get(lang)
    if not config:
        return {
            "status": "error",
            "output": f"Execution for language '{lang}' is not configured yet."
        }
        
    executable = get_executable_from_config(config)
        
    if executable and not shutil.which(executable):
        return {
            "status": "error",
            "output": f"System Error: '{executable}' is not installed or not in PATH.\nTo run {request.language} code, you must install {executable} on the server running this app."
        }

    with tempfile.TemporaryDirectory() as temp_dir:
        return execute_in_temp_dir(config, temp_dir, request.code_content)

