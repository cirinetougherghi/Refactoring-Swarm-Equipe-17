"""
Test que les imports fonctionnent correctement
Script de diagnostic pour le TP Refactoring Swarm
"""

import sys
from pathlib import Path

def test_imports():
    """Teste tous les imports nécessaires pour le projet"""
    
    print("=" * 60)
    print("🧪 TEST DES IMPORTS - TP REFACTORING SWARM")
    print("=" * 60)
    print()
    
    # Vérification du chemin Python
    print("📂 Répertoire courant:", Path.cwd())
    print("🐍 Version Python:", sys.version)
    print()
    
    success_count = 0
    total_tests = 0
    errors = []
    
    # Test 1: Import du logger principal
    print("Test 1: Import du logger principal...")
    total_tests += 1
    try:
        from src.utils.logger import log_experiment, ActionType
        print("   ✅ Import logger.py OK")
        print(f"   ✅ log_experiment: {type(log_experiment)}")
        print(f"   ✅ ActionType: {type(ActionType)}")
        success_count += 1
    except ImportError as e:
        print(f"   ❌ Import logger.py ÉCHOUÉ: {e}")
        errors.append(("logger.py", str(e)))
    except Exception as e:
        print(f"   ❌ Erreur inattendue: {e}")
        errors.append(("logger.py", str(e)))
    print()
    
    # Test 2: Import des helpers de logging
    print("Test 2: Import des helpers de logging...")
    total_tests += 1
    try:
        from src.utils.logging_helpers import log_auditor
        print("   ✅ Import logging_helpers.py OK")
        print(f"   ✅ log_auditor: {type(log_auditor)}")
        success_count += 1
    except ImportError as e:
        print(f"   ❌ Import logging_helpers.py ÉCHOUÉ: {e}")
        errors.append(("logging_helpers.py", str(e)))
    except Exception as e:
        print(f"   ❌ Erreur inattendue: {e}")
        errors.append(("logging_helpers.py", str(e)))
    print()
    
    # Test 3: Import depuis src.utils (via __init__.py)
    print("Test 3: Import depuis src.utils (package)...")
    total_tests += 1
    try:
        from src.utils import log_experiment, ActionType
        print("   ✅ Import depuis src.utils OK")
        print("   ✅ Le fichier __init__.py est correctement configuré")
        success_count += 1
    except ImportError as e:
        print(f"   ❌ Import depuis src.utils ÉCHOUÉ: {e}")
        print("   💡 Vérifiez que src/utils/__init__.py existe et exporte les bonnes fonctions")
        errors.append(("src.utils package", str(e)))
    except Exception as e:
        print(f"   ❌ Erreur inattendue: {e}")
        errors.append(("src.utils package", str(e)))
    print()
    
    # Test 4: Vérification de la structure des dossiers
    print("Test 4: Vérification de la structure des dossiers...")
    total_tests += 1
    required_paths = [
        "src/utils/logger.py",
        "src/utils/__init__.py",
        "logs"
    ]
    
    all_paths_exist = True
    for path_str in required_paths:
        path = Path(path_str)
        if path.exists():
            print(f"   ✅ {path_str} existe")
        else:
            print(f"   ❌ {path_str} MANQUANT")
            all_paths_exist = False
            errors.append((path_str, "Fichier ou dossier manquant"))
    
    if all_paths_exist:
        success_count += 1
        print("   ✅ Structure des dossiers OK")
    else:
        print("   ❌ Structure des dossiers incomplète")
    print()
    
    # Test 5: Test fonctionnel du logger
    print("Test 5: Test fonctionnel du logger...")
    total_tests += 1
    try:
        from src.utils.logger import log_experiment, ActionType
        
        # Tentative d'enregistrement d'un log de test
        log_experiment(
            agent_name="Test_Agent",
            model_used="gemini-test",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Test prompt",
                "output_response": "Test response",
                "test": True
            },
            status="SUCCESS"
        )
        print("   ✅ log_experiment() fonctionne correctement")
        print("   ✅ Vérifiez logs/experiment_data.json pour voir l'entrée de test")
        success_count += 1
    except Exception as e:
        print(f"   ❌ Erreur lors de l'appel à log_experiment(): {e}")
        errors.append(("log_experiment function", str(e)))
    print()
    
    # Résumé
    print("=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Tests réussis: {success_count}/{total_tests}")
    print()
    
    if success_count == total_tests:
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("   Votre environnement est correctement configuré.")
        print()
        return True
    else:
        print(f"❌ {total_tests - success_count} TEST(S) ÉCHOUÉ(S)")
        print()
        
        if errors:
            print("🔍 DÉTAILS DES ERREURS:")
            print()
            for i, (component, error) in enumerate(errors, 1):
                print(f"{i}. {component}:")
                print(f"   {error}")
                print()
            
            print("💡 SOLUTIONS POSSIBLES:")
            print()
            
            # Diagnostics spécifiques
            if any("logger.py" in err[0] for err in errors):
                print("• Pour logger.py manquant:")
                print("  - Vérifiez que le fichier src/utils/logger.py existe")
                print("  - Vérifiez que vous êtes dans le bon répertoire")
                print()
            
            if any("__init__.py" in err[0] or "package" in err[0] for err in errors):
                print("• Pour les problèmes d'import de package:")
                print("  - Créez src/__init__.py (peut être vide)")
                print("  - Créez src/utils/__init__.py avec:")
                print("    from .logger import log_experiment, ActionType")
                print()
            
            if any("logging_helpers" in err[0] for err in errors):
                print("• Pour logging_helpers.py:")
                print("  - Vérifiez que le fichier existe")
                print("  - Vérifiez qu'il contient bien la fonction log_auditor")
                print()
        
        return False


if __name__ == "__main__":
    success = test_imports()
    
    # Code de sortie pour intégration dans des scripts
    sys.exit(0 if success else 1)