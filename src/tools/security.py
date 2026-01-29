import os
from pathlib import Path


def get_sandbox_path():
    """
    Retourne le chemin absolu du dossier sandbox
    
    Returns:
        Path: Chemin absolu vers /sandbox
    """
    # Le dossier sandbox est à la racine du projet
    project_root = Path(__file__).parent.parent.parent
    sandbox_path = project_root / "sandbox"
    
    # Créer le dossier s'il n'existe pas
    sandbox_path.mkdir(exist_ok=True)
    
    return sandbox_path.resolve()


def is_safe_path(filepath):
    """
    Vérifie si un chemin est dans le dossier sandbox (sécurité)
    
    Args:
        filepath (str): Chemin du fichier à vérifier
        
    Returns:
        bool: True si le chemin est sûr, False sinon
        
    Examples:
        >>> is_safe_path("./sandbox/test.py")
        True
        >>> is_safe_path("../../../etc/passwd")
        False
    """
    try:
        # Convertir en chemin absolu
        abs_filepath = Path(filepath).resolve()
        sandbox = get_sandbox_path()
        
        # Vérifier si le fichier est dans sandbox ou un sous-dossier
        return str(abs_filepath).startswith(str(sandbox))
        
    except Exception as e:
        print(f"Erreur lors de la vérification du chemin: {e}")
        return False


def validate_path_or_raise(filepath, operation="read"):
    """
    Valide un chemin et lève une exception si dangereux
    
    Args:
        filepath (str): Chemin à valider
        operation (str): Type d'opération ("read" ou "write")
        
    Raises:
        SecurityError: Si le chemin est en dehors de sandbox
    """
    if not is_safe_path(filepath):
        raise SecurityError(
            f"SECURITE: Tentative d'accès interdit en dehors de sandbox!\n"
            f"Chemin demandé: {filepath}\n"
            f"Opération: {operation}"
        )


class SecurityError(Exception):
    """Exception levée lors d'une violation de sécurité"""
    pass


# Test de la fonction
if __name__ == "__main__":
    print("=== Test des outils de sécurité ===\n")
    
    # Test 1: Chemin valide
    safe_path = "./sandbox/test.py"
    print(f"Test 1: {safe_path}")
    print(f"Résultat: {'✓ Sûr' if is_safe_path(safe_path) else '✗ Dangereux'}\n")
    
    # Test 2: Chemin dangereux
    unsafe_path = "../../../etc/passwd"
    print(f"Test 2: {unsafe_path}")
    print(f"Résultat: {'✓ Sûr' if is_safe_path(unsafe_path) else '✗ Dangereux'}\n")
    
    # Test 3: Validation avec exception
    print("Test 3: Validation avec exception")
    try:
        validate_path_or_raise(unsafe_path, "write")
    except SecurityError as e:
        print(f"✓ Exception levée correctement:\n{e}")