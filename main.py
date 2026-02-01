"""
Point d'entrée principal du Refactoring Swarm
Système multi-agents de refactoring automatique de code Python

Usage:
    python main.py --target_dir ./sandbox/dataset_inconnu

Responsable : Lead Dev (Orchestrateur)
Date : 2026-01-10
Version : 1.0
"""

import argparse
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

from src.orchestrator import Orchestrator


def validate_environment():
    """
    Vérifie que l'environnement est correctement configuré.
    
    Returns:
        bool: True si tout est OK, False sinon
    """
    print("\n" + "="*80)
    print("VÉRIFICATION DE L'ENVIRONNEMENT")
    print("="*80)
    
    # Vérifier la clé API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERREUR: GOOGLE_API_KEY non trouvée dans le fichier .env")
        print("\nSolution:")
        print("  1. Créez un fichier .env à la racine du projet")
        print("  2. Ajoutez: GOOGLE_API_KEY=votre_clé_ici")
        print("  3. Obtenez une clé sur: https://aistudio.google.com/app/apikey")
        return False
    
    print(f"✓ Clé API Google Gemini détectée ({api_key[:20]}...)")
    
    # Vérifier que les dossiers nécessaires existent
    required_dirs = ["logs", "sandbox"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"⚠️  Dossier '{dir_name}' manquant - Création...")
            os.makedirs(dir_name, exist_ok=True)
            print(f"✓ Dossier '{dir_name}' créé")
        else:
            print(f"✓ Dossier '{dir_name}' existe")
    
    print("="*80)
    print("✅ Environnement validé\n")
    return True


def parse_arguments():
    """
    Parse les arguments de la ligne de commande.
    
    Returns:
        argparse.Namespace: Arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="The Refactoring Swarm - Système multi-agents de refactoring automatique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py --target_dir ./sandbox/dataset_inconnu
  python main.py --target_dir ./sandbox/test_dataset --max_iterations 5

Notes:
  - Le dossier cible doit contenir des fichiers .py
  - Les logs seront sauvegardés dans logs/experiment_data.json
  - Le système s'arrête après max_iterations (défaut: 10)
        """
    )
    
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Dossier contenant les fichiers Python à refactoriser (OBLIGATOIRE)"
    )
    
    parser.add_argument(
        "--max_iterations",
        type=int,
        default=10,
        help="Nombre maximum d'itérations par fichier (défaut: 10)"
    )
    
    return parser.parse_args()


def validate_target_directory(target_dir):
    """
    Vérifie que le dossier cible est valide.
    
    Args:
        target_dir (str): Chemin vers le dossier cible
        
    Returns:
        bool: True si valide, False sinon
    """
    # Vérifier que le dossier existe
    if not os.path.exists(target_dir):
        print(f"❌ ERREUR: Le dossier '{target_dir}' n'existe pas")
        print("\nSolution:")
        print(f"  mkdir {target_dir}")
        print(f"  # Puis ajoutez vos fichiers Python dans ce dossier")
        return False
    
    # Vérifier que c'est bien un dossier
    if not os.path.isdir(target_dir):
        print(f"❌ ERREUR: '{target_dir}' n'est pas un dossier")
        return False
    
    # Vérifier qu'il contient au moins un fichier Python
    python_files = [f for f in os.listdir(target_dir) if f.endswith(".py")]
    if not python_files:
        print(f"⚠️  ATTENTION: Aucun fichier Python (.py) trouvé dans '{target_dir}'")
        print("\nLe système va quand même démarrer, mais il n'y a rien à traiter.")
        response = input("Continuer quand même ? (o/n): ")
        if response.lower() != 'o':
            return False
    
    return True


def main():
    """
    Point d'entrée principal du système multi-agents.
    """
    # Charger les variables d'environnement
    load_dotenv()
    
    # Afficher le header
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "    THE REFACTORING SWARM - SYSTÈME MULTI-AGENTS".center(78) + "█")
    print("█" + "    École nationale Supérieure d'Informatique".center(78) + "█")
    print("█" + "    TP IGL 2025-2026".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80 + "\n")
    
    # Valider l'environnement
    if not validate_environment():
        sys.exit(1)
    
    # Parser les arguments
    args = parse_arguments()
    
    print("="*80)
    print("CONFIGURATION DU SYSTÈME")
    print("="*80)
    print(f"Dossier cible     : {args.target_dir}")
    print(f"Max iterations    : {args.max_iterations}")
    print("="*80 + "\n")
    
    # Valider le dossier cible
    if not validate_target_directory(args.target_dir):
        sys.exit(1)
    
    # Configurer Gemini
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    # Initialiser et lancer l'orchestrateur
    print("="*80)
    print("DÉMARRAGE DU SYSTÈME")
    print("="*80 + "\n")
    
    try:
        orchestrator = Orchestrator(
            target_dir=args.target_dir,
            max_iterations=args.max_iterations
        )
        
        summary = orchestrator.run()
        
        # Afficher le résumé final
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "    RÉSULTAT FINAL".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80)
        print()
        
        total = summary.get("total_files", 0)
        validated = summary.get("files_validated", 0)
        failed = summary.get("files_failed", 0)
        success_rate = summary.get("success_rate", 0)
        
        print(f"Fichiers traités : {total}")
        print(f"Validés          : {validated}")
        print(f"Échoués          : {failed}")
        print(f"Taux de succès   : {success_rate:.1f}%")
        print()
        
        # Déterminer le code de sortie et le message
        if total == 0:
            print("⚠️  ATTENTION: Aucun fichier traité")
            exit_code = 1
        elif validated == total:
            print("✅ SUCCÈS TOTAL - Tous les fichiers ont été validés !")
            exit_code = 0
        elif validated > 0:
            print(f"⚠️  SUCCÈS PARTIEL - {validated}/{total} fichiers validés")
            exit_code = 0
        else:
            print("❌ ÉCHEC - Aucun fichier validé")
            exit_code = 1
        
        print()
        print("█"*80)
        print()
        
        # Afficher l'emplacement des logs
        print("📊 Logs et données sauvegardés dans: logs/experiment_data.json")
        print()
        
        sys.exit(exit_code)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERRUPTION UTILISATEUR")
        print("Le système a été arrêté manuellement (Ctrl+C)")
        print()
        sys.exit(130)
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        print("\nTraceback complet:")
        import traceback
        traceback.print_exc()
        print("\n" + "="*80)
        print("Le système a rencontré une erreur inattendue.")
        print("Vérifiez les logs ci-dessus pour plus de détails.")
        print("="*80 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()