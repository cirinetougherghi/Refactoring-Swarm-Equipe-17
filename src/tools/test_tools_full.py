import os
import sys
import json
import subprocess

# Ajouter le root du projet au path pour trouver tools
sys.path.insert(0, os.path.abspath("."))

# Importer les outils
from src.tools.analysis_tools import run_pylint, run_pytest
from src.tools.file_tools import read_file, write_file
from src.utils.logger import log_experiment, ActionType

# Dossier sandbox
SANDBOX_DIR = "sandbox"


def test_all_tools():
    """
    Teste tous les outils sur tous les fichiers Python dans sandbox
    Génère un rapport JSON avec les résultats
    """
    # Log start of full test suite
    log_experiment(
        agent_name="Test_Suite_Runner",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "operation": "full_test_suite_start",
            "input_prompt": f"Starting comprehensive test suite on all files in {SANDBOX_DIR}",
            "output_response": "Test suite initialized",
            "sandbox_directory": SANDBOX_DIR
        },
        status="SUCCESS"
    )
    
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
        log_experiment(
            agent_name="Test_Suite_Runner",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "operation": "scan_sandbox",
                "input_prompt": f"Scanning for Python files in {SANDBOX_DIR}",
                "output_response": "No Python files found in sandbox",
                "files_found": 0
            },
            status="FAILURE"
        )
        print(f"Aucun fichier Python trouvé dans {SANDBOX_DIR}")
        return
    
    log_experiment(
        agent_name="Test_Suite_Runner",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "operation": "scan_sandbox",
            "input_prompt": f"Scanning for Python files in {SANDBOX_DIR}",
            "output_response": f"Found {len(python_files)} Python files",
            "files_found": len(python_files),
            "file_list": python_files
        },
        status="SUCCESS"
    )
    
    for f in python_files:
        path = os.path.join(SANDBOX_DIR, f)
        print(f"--- Traitement de {f} ---")
        
        try:
            # Etape 1: Executer Pylint
            pylint_result = run_pylint(path)
            score = pylint_result.get("score", 0)
            print(f"Score Pylint: {score}")
            
            # Etape 2: Lire et copier le fichier
            content = read_file(path)
            copy_path = os.path.join(SANDBOX_DIR, f"{f}_copy.py")
            write_file(copy_path, content)
            print(f"Copie créée: {copy_path}")
            
            # Etape 3: Executer Pytest
            tests = run_pytest(path)
            print(f"Résultats Pytest: {tests}")
            
            # Etape 4: Mettre à jour le rapport
            report["files"][f] = {
                "pylint_score": score, 
                **tests
            }
            report["summary"]["total_files"] += 1
            report["summary"]["total_passed"] += tests["passed"]
            report["summary"]["total_failed"] += tests["failed"]
            
            # Log successful file processing
            log_experiment(
                agent_name="Test_Suite_Runner",
                model_used="N/A",
                action=ActionType.ANALYSIS,
                details={
                    "operation": "process_file",
                    "file_processed": f,
                    "input_prompt": f"Processing complete test suite for: {f}",
                    "output_response": f"File processed: Pylint={score}/10, Tests passed={tests['passed']}, failed={tests['failed']}",
                    "pylint_score": score,
                    "tests_passed": tests["passed"],
                    "tests_failed": tests["failed"]
                },
                status="SUCCESS"
            )
            
        except Exception as e:
            # Log file processing error
            log_experiment(
                agent_name="Test_Suite_Runner",
                model_used="N/A",
                action=ActionType.DEBUG,
                details={
                    "operation": "process_file",
                    "file_processed": f,
                    "input_prompt": f"Processing test suite for: {f}",
                    "output_response": f"Error processing file: {str(e)}",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                },
                status="FAILURE"
            )
            print(f"Erreur lors du traitement de {f}: {e}")
    
    # Sauvegarder le rapport JSON à la racine du projet
    report_path = "report.json"
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Rapport report.json généré dans {report_path}")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        
        # Log successful report generation
        log_experiment(
            agent_name="Test_Suite_Runner",
            model_used="N/A",
            action=ActionType.GENERATION,
            details={
                "operation": "generate_report",
                "input_prompt": "Generating final test suite report",
                "output_response": f"Report generated successfully: {report['summary']['total_files']} files processed",
                "report_path": report_path,
                "total_files": report["summary"]["total_files"],
                "total_passed": report["summary"]["total_passed"],
                "total_failed": report["summary"]["total_failed"]
            },
            status="SUCCESS"
        )
        
    except Exception as e:
        # Log report generation error
        log_experiment(
            agent_name="Test_Suite_Runner",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "operation": "generate_report",
                "input_prompt": "Generating final test suite report",
                "output_response": f"Error generating report: {str(e)}",
                "error_type": type(e).__name__
            },
            status="FAILURE"
        )
        print(f"Erreur lors de la génération du rapport: {e}")


if __name__ == "__main__":
    test_all_tools()