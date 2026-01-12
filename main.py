"""
Point d'entree principal du Refactoring Swarm
Responsable : Lead Dev (Orchestrateur)
Date : 2026-01-10

Usage:
    python main.py --target_dir ./sandbox/dataset_inconnu
"""

import argparse
import sys
import os
from dotenv import load_dotenv
import google.generativeai as genai

from src.orchestrator import Orchestrator
from src.utils.logger import log_experiment, ActionType


def main():
    """Point d'entree principal."""
    
    parser = argparse.ArgumentParser(
        description="Refactoring Swarm - Systeme multi-agents de refactoring automatique"
    )
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Dossier contenant les fichiers Python a analyser et corriger"
    )
    parser.add_argument(
        "--max_iterations",
        type=int,
        default=10,
        help="Nombre maximum d'iterations par fichier (defaut: 10)"
    )
    
    args = parser.parse_args()
    
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERREUR : Cle API non trouvee dans le fichier .env")
        print("Ajoutez GOOGLE_API_KEY=votre_cle dans le fichier .env")
        sys.exit(1)
    
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"ERREUR lors de la configuration de l'API : {e}")
        sys.exit(1)
    
    if not os.path.exists(args.target_dir):
        print(f"ERREUR : Dossier '{args.target_dir}' introuvable")
        sys.exit(1)
    
    log_experiment(
        agent_name="System",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Starting Refactoring Swarm on {args.target_dir}",
            "output_response": f"Target directory: {args.target_dir}, Max iterations: {args.max_iterations}",
            "target_dir": args.target_dir,
            "max_iterations": args.max_iterations
        },
        status="SUCCESS"
    )
    
    print("\n" + "="*80)
    print("REFACTORING SWARM - SYSTEME MULTI-AGENTS")
    print("="*80)
    print(f"Dossier cible : {args.target_dir}")
    print(f"Max iterations : {args.max_iterations}")
    print("="*80 + "\n")
    
    try:
        orchestrator = Orchestrator(
            target_dir=args.target_dir,
            max_iterations=args.max_iterations
        )
        
        results = orchestrator.run()
        
        log_experiment(
            agent_name="System",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Workflow completed",
                "output_response": f"Files validated: {results['files_validated']}/{results['total_files']}",
                "total_files": results["total_files"],
                "files_validated": results["files_validated"],
                "files_failed": results["files_failed"],
                "success_rate": results["success_rate"]
            },
            status="SUCCESS" if results["files_validated"] == results["total_files"] else "PARTIAL_SUCCESS"
        )
        
        if results["files_validated"] == results["total_files"]:
            print("\nMISSION ACCOMPLIE - Tous les fichiers valides !")
            sys.exit(0)
        else:
            print(f"\nMISSION PARTIELLE - {results['files_validated']}/{results['total_files']} fichiers valides")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nInterruption par l'utilisateur")
        log_experiment(
            agent_name="System",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "User interrupt",
                "output_response": "Workflow interrupted by user",
                "error": "KeyboardInterrupt"
            },
            status="FAILURE"
        )
        sys.exit(130)
    
    except Exception as e:
        print(f"\nERREUR CRITIQUE : {e}")
        log_experiment(
            agent_name="System",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Critical error",
                "output_response": str(e),
                "error": str(e)
            },
            status="FAILURE"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()