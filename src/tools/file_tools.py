import os


SANDBOX_DIR = os.path.abspath("sandbox")


def _is_inside_sandbox(path: str) -> bool:
    """
    Vérifie si un chemin est strictement à l'intérieur du dossier sandbox/
    """
    abs_path = os.path.abspath(path)
    return abs_path.startswith(SANDBOX_DIR)


def read_file(path: str) -> str:
    """
    Lit le contenu d'un fichier situé dans sandbox/
    """
    if not _is_inside_sandbox(path):
        raise PermissionError("Lecture hors du dossier sandbox interdite")

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    """
    Écrit du contenu dans un fichier situé dans sandbox/
    """
    if not _is_inside_sandbox(path):
        raise PermissionError("Écriture hors du dossier sandbox interdite")

    # créer le dossier parent si nécessaire
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
 
 