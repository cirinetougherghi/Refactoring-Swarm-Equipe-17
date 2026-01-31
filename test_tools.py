"""
Script de test manuel des outils du Refactoring Swarm.

Ce script teste :
- run_pylint : Analyse statique
- run_pytest : Exécution des tests
- read_file / write_file : Manipulation de fichiers

Usage:
    python test_tools.py

Auteur: Équipe Refactoring Swarm
Date: 2026-01-10
"""

import os
import json
import sys

# Importer les outils depuis src/
from src.tools.analysis_tools import run_pylint, run_pytest
from src.tools.file_tools import read_file, write_file

SANDBOX_DIR = "sandbox"


def test_all_tools():
    """
    Teste tous les outils sur tous les fichiers Python dans sandbox/
    Génère un rapport JSON avec les résultats
    """
    print("="*80)
    print("TEST DES OUTILS - REFACTORING SWARM")
    print("="*80)
    
    # Vérifier que le dossier sandbox existe
    if not os.path.exists(SANDBOX_DIR):
        print(f"ERREUR: Le dossier '{SANDBOX_DIR}' n'existe pas")
        print("Créez-le et ajoutez des fichiers Python pour tester")
        sys.exit(1)
    
    report = {
        "files": {}, 
        "summary": {
            "total_files": 0, 
            "total_passed": 0, 
            "total_failed": 0
        }
    }
    
    # Parcourir tous les fichiers Python dans sandbox
    python_files = [f for f in os.listdir(SANDBOX_DIR) if f.endswith(".py")]
    
    if not python_files:
        print(f"ATTENTION: Aucun fichier Python trouvé dans '{SANDBOX_DIR}'")
        sys.exit(0)
    
    print(f"\nFichiers Python trouvés : {len(python_files)}\n")
    
    for f in python_files:
        path = os.path.join(SANDBOX_DIR, f)
        print(f"{'─'*80}")
        print(f"Traitement de : {f}")
        print(f"{'─'*80}")
        
        # ÉTAPE 1 : Exécuter Pylint
        try:
            pylint_result = run_pylint(path)
            score = pylint_result.get("score", 0.0)
            print(f"✓ Pylint Score : {score}/10.0")
        except Exception as e:
            print(f"✗ Pylint ERREUR : {e}")
            score = 0.0
        
        # ÉTAPE 2 : Lire et copier le fichier
        try:
            content = read_file(path)
            copy_path = os.path.join(SANDBOX_DIR, f"COPY_{f}")
            write_file(copy_path, content)
            print(f"✓ Fichier copié : {copy_path}")
        except Exception as e:
            print(f"✗ Copie ERREUR : {e}")
        
        # ÉTAPE 3 : Exécuter Pytest
        try:
            pytest_result = run_pytest(path)
            passed = pytest_result.get("passed", 0)
            failed = pytest_result.get("failed", 0)
            print(f"✓ Pytest : {passed} passés, {failed} échoués")
        except Exception as e:
            print(f"✗ Pytest ERREUR : {e}")
            pytest_result = {"passed": 0, "failed": 0}
        
        # ÉTAPE 4 : Mettre à jour le rapport
        report["files"][f] = {
            "pylint_score": score,
            "tests_passed": pytest_result.get("passed", 0),
            "tests_failed": pytest_result.get("failed", 0)
        }
        report["summary"]["total_files"] += 1
        report["summary"]["total_passed"] += pytest_result.get("passed", 0)
        report["summary"]["total_failed"] += pytest_result.get("failed", 0)
        
        print()
    
    # Sauvegarder le rapport JSON à la racine du projet
    report_path = "tools_test_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("="*80)
    print("RÉSUMÉ FINAL")
    print("="*80)
    print(f"Fichiers testés : {report['summary']['total_files']}")
    print(f"Tests passés : {report['summary']['total_passed']}")
    print(f"Tests échoués : {report['summary']['total_failed']}")
    print(f"\nRapport sauvegardé : {report_path}")
    print("="*80)
    
    return report


if __name__ == "__main__":
    test_all_tools()