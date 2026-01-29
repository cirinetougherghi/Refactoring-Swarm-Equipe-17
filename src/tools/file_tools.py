import os
from src.utils.logger import log_experiment, ActionType

SANDBOX_DIR = os.path.abspath("sandbox")


def _is_inside_sandbox(path: str) -> bool:
    """
    Vérifie si un chemin est strictement à l'intérieur du dossier sandbox/
    """
    abs_path = os.path.abspath(path)
    is_safe = abs_path.startswith(SANDBOX_DIR)
    
    # Log security check
    log_experiment(
        agent_name="Security_Check",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "operation": "sandbox_validation",
            "file_path": path,
            "input_prompt": f"Validating if path is inside sandbox: {path}",
            "output_response": f"Path is {'SAFE (inside sandbox)' if is_safe else 'BLOCKED (outside sandbox)'}",
            "is_safe": is_safe,
            "absolute_path": abs_path,
            "sandbox_root": SANDBOX_DIR
        },
        status="SUCCESS" if is_safe else "FAILURE"
    )
    
    return is_safe


def read_file(path: str) -> str:
    """
    Lit le contenu d'un fichier situé dans sandbox/
    """
    try:
        if not _is_inside_sandbox(path):
            raise PermissionError("Lecture hors du dossier sandbox interdite")
        
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Fichier introuvable : {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Log successful read
        log_experiment(
            agent_name="FileSystem_Tool",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "operation": "read_file",
                "file_path": path,
                "input_prompt": f"Reading file content from: {path}",
                "output_response": f"Successfully read {len(content)} characters from {os.path.basename(path)}",
                "file_size_chars": len(content),
                "file_name": os.path.basename(path),
                "content_preview": content[:150] + "..." if len(content) > 150 else content
            },
            status="SUCCESS"
        )
        
        return content
        
    except PermissionError as e:
        log_experiment(
            agent_name="FileSystem_Tool",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "operation": "read_file",
                "file_path": path,
                "input_prompt": f"Attempting to read file: {path}",
                "output_response": f"Permission denied: {str(e)}",
                "error_type": "PermissionError"
            },
            status="FAILURE"
        )
        raise
        
    except FileNotFoundError as e:
        log_experiment(
            agent_name="FileSystem_Tool",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "operation": "read_file",
                "file_path": path,
                "input_prompt": f"Attempting to read file: {path}",
                "output_response": f"File not found: {str(e)}",
                "error_type": "FileNotFoundError"
            },
            status="FAILURE"
        )
        raise
        
    except Exception as e:
        log_experiment(
            agent_name="FileSystem_Tool",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "operation": "read_file",
                "file_path": path,
                "input_prompt": f"Attempting to read file: {path}",
                "output_response": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__
            },
            status="FAILURE"
        )
        raise


def write_file(path: str, content: str) -> None:
    """
    Écrit du contenu dans un fichier situé dans sandbox/
    """
    try:
        if not _is_inside_sandbox(path):
            raise PermissionError("Écriture hors du dossier sandbox interdite")
        
        # créer le dossier parent si nécessaire
        parent_dir = os.path.dirname(path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Log successful write
        log_experiment(
            agent_name="FileSystem_Tool",
            model_used="N/A",
            action=ActionType.FIX,
            details={
                "operation": "write_file",
                "file_path": path,
                "input_prompt": f"Writing content to file: {path}",
                "output_response": f"Successfully wrote {len(content)} characters to {os.path.basename(path)}",
                "content_size_chars": len(content),
                "file_name": os.path.basename(path),
                "content_preview": content[:150] + "..." if len(content) > 150 else content
            },
            status="SUCCESS"
        )
        
    except PermissionError as e:
        log_experiment(
            agent_name="FileSystem_Tool",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "operation": "write_file",
                "file_path": path,
                "input_prompt": f"Attempting to write to file: {path}",
                "output_response": f"Permission denied: {str(e)}",
                "error_type": "PermissionError"
            },
            status="FAILURE"
        )
        raise
        
    except Exception as e:
        log_experiment(
            agent_name="FileSystem_Tool",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "operation": "write_file",
                "file_path": path,
                "input_prompt": f"Attempting to write to file: {path}",
                "output_response": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__
            },
            status="FAILURE"
        )
        raise