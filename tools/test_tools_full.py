import os
import sys
import json
import subprocess

# Ajouter le root du projet au path pour trouver tools
sys.path.insert(0, os.path.abspath("."))

# Importer les outils
from tools.analysis_tools import run_pylint, run_pytest
from tools.file_tools import read_file, write_file

# Dossier sandbox
SANDBOX_DIR = "sandbox"


def test_all_tools():
    """
    Teste tous les outils sur tous les fichiers Python dans sandbox
    Génère un rapport JSON avec les résultats
    """
    report = {
        "files": {}, 
        "summary": {
            "total_files": 0, 
            "total_passed": 0, 
            "total_failed": 0
        }
    }
    
    # Parcourir tous les fichiers Python dans sandbox
    for f in os.listdir(SANDBOX_DIR):
        if f.endswith(".py"):
            path = os.path.join(SANDBOX_DIR, f)
            print(f"--- Traitement de {f} ---")
            
            # Etape 1: Executer Pylint
            score = run_pylint(path)
            print(f"Score Pylint: {score}")
            
            # Etape 2: Lire et copier le fichier
            content = read_file(path)
            copy_path = os.path.join(SANDBOX_DIR, f"{f}_copy.py")
            write_file(copy_path, content)
            print(f"Copie creee: {copy_path}")
            
            # Etape 3: Executer Pytest
            tests = run_pytest(path)
            print(f"Resultats Pytest: {tests}")
            
            # Etape 4: Mettre a jour le rapport
            report["files"][f] = {
                "pylint_score": score, 
                **tests
            }
            report["summary"]["total_files"] += 1
            report["summary"]["total_passed"] += tests["passed"]
            report["summary"]["total_failed"] += tests["failed"]
    
    # Sauvegarder le rapport JSON a la racine du projet
    report_path = "report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Rapport report.json genere dans {report_path}")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_all_tools()