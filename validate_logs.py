"""
Script de validation des logs
Créé par: Data Officer
Conforme au protocole de logging du TP IGL 2025-2026
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def validate_experiment_logs():
    """Valide le fichier experiment_data.json selon les spécifications du TP"""
    
    log_file = Path("logs/experiment_data.json")
    
    print("=" * 60)
    print("🔍 VALIDATION DES LOGS - TP REFACTORING SWARM")
    print("=" * 60)
    print()
    
    # Vérification de l'existence du fichier
    if not log_file.exists():
        print("❌ ERREUR CRITIQUE : experiment_data.json n'existe pas!")
        print(f"   Chemin attendu : {log_file.absolute()}")
        print()
        print("💡 Conseil : Assurez-vous que le dossier logs/ existe")
        print("   et que vos agents utilisent bien log_experiment().")
        return False
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Vérification que le fichier n'est pas vide
        if not data:
            print("⚠️  ATTENTION : Le fichier de logs est vide!")
            print("   Aucune interaction avec les LLM n'a été enregistrée.")
            print()
            print("💡 Conseil : Vérifiez que vos agents appellent bien log_experiment()")
            print("   après chaque interaction avec le modèle.")
            return False
        
        if not isinstance(data, list):
            print("❌ ERREUR : Le fichier doit contenir une liste d'entrées JSON")
            return False
        
        print(f"✅ Fichier trouvé : {log_file}")
        print(f"✅ Format JSON valide")
        print(f"✅ Nombre d'entrées : {len(data)}")
        print()
        
        # Vérification détaillée de chaque entrée
        required_fields = ['agent', 'model', 'action', 'details', 'status', 'timestamp']
        valid_actions = ['ANALYSIS', 'GENERATION', 'DEBUG', 'FIX']
        valid_statuses = ['SUCCESS', 'FAILURE', 'ERROR', 'PARTIAL']
        
        errors = 0
        warnings = 0
        
        print("🔎 Vérification détaillée des entrées...")
        print()
        
        for i, entry in enumerate(data):
            entry_errors = []
            entry_warnings = []
            
            # Vérifier les champs obligatoires
            for field in required_fields:
                if field not in entry:
                    entry_errors.append(f"Champ obligatoire '{field}' manquant")
            
            # Vérifier le type d'action
            if 'action' in entry:
                action = entry['action']
                if action not in valid_actions:
                    entry_errors.append(
                        f"Action '{action}' invalide. Attendu: {', '.join(valid_actions)}"
                    )
            
            # Vérifier le statut
            if 'status' in entry:
                status = entry['status']
                if status not in valid_statuses:
                    entry_warnings.append(
                        f"Status '{status}' non standard. Recommandé: {', '.join(valid_statuses)}"
                    )
            
            # Vérifier le nom de l'agent
            if 'agent' in entry and not entry['agent']:
                entry_errors.append("Le nom de l'agent ne peut pas être vide")
            
            # Vérifier le modèle utilisé
            if 'model' in entry and not entry['model']:
                entry_warnings.append("Le nom du modèle n'est pas spécifié")
            
            # Vérifier les détails (CRITIQUE pour l'évaluation)
            if 'details' in entry:
                details = entry['details']
                
                if not isinstance(details, dict):
                    entry_errors.append("Le champ 'details' doit être un dictionnaire")
                else:
                    # OBLIGATOIRE selon le document
                    if 'input_prompt' not in details or not details.get('input_prompt'):
                        entry_errors.append(
                            "CRITIQUE: 'input_prompt' manquant ou vide dans details"
                        )
                    
                    # ✅ MODIFICATION ICI : output_response peut être vide si status == ERROR ou PARTIAL
                    if 'output_response' not in details:
                        entry_errors.append(
                            "CRITIQUE: 'output_response' manquant dans details"
                        )
                    elif not details.get('output_response'):
                        # output_response est vide, vérifier le status
                        status = entry.get('status', '')
                        if status not in ['ERROR', 'PARTIAL']:
                            entry_errors.append(
                                f"CRITIQUE: 'output_response' vide alors que status={status} (devrait être ERROR ou PARTIAL)"
                            )
                        # Sinon c'est OK (erreur API, donc pas de réponse)
            
            # Vérifier le timestamp
            if 'timestamp' in entry:
                try:
                    # Vérifier que c'est un timestamp valide
                    datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    entry_warnings.append("Format de timestamp invalide ou non-ISO")
            
            # Afficher les erreurs/warnings pour cette entrée
            if entry_errors:
                print(f"❌ Entrée #{i}:")
                for error in entry_errors:
                    print(f"   • {error}")
                errors += len(entry_errors)
            
            if entry_warnings:
                print(f"⚠️  Entrée #{i}:")
                for warning in entry_warnings:
                    print(f"   • {warning}")
                warnings += len(entry_warnings)
        
        print()
        print("=" * 60)
        
        # Résumé de la validation
        if errors == 0 and warnings == 0:
            print("✅ VALIDATION RÉUSSIE !")
            print("   Tous les logs sont conformes au protocole.")
        elif errors == 0:
            print(f"✅ VALIDATION RÉUSSIE avec {warnings} avertissement(s)")
            print("   Les logs sont conformes mais peuvent être améliorés.")
        else:
            print(f"❌ VALIDATION ÉCHOUÉE : {errors} erreur(s) critique(s)")
            if warnings > 0:
                print(f"   + {warnings} avertissement(s)")
            print()
            print("⚠️  ATTENTION : Votre note 'Qualité des Données' sera impactée!")
            
        print()
        print("=" * 60)
        
        # Statistiques détaillées
        if errors == 0:
            print("📊 STATISTIQUES DES LOGS:")
            print()
            
            # Comptage par agent
            agents = {}
            actions = {}
            statuses = {}
            models = {}
            
            for entry in data:
                agent = entry.get('agent', 'Unknown')
                action = entry.get('action', 'Unknown')
                status = entry.get('status', 'Unknown')
                model = entry.get('model', 'Unknown')
                
                agents[agent] = agents.get(agent, 0) + 1
                actions[action] = actions.get(action, 0) + 1
                statuses[status] = statuses.get(status, 0) + 1
                models[model] = models.get(model, 0) + 1
            
            print("🤖 Activité par agent:")
            for agent, count in sorted(agents.items()):
                print(f"   • {agent}: {count} action(s)")
            
            print()
            print("⚙️  Répartition par type d'action:")
            for action, count in sorted(actions.items()):
                print(f"   • {action}: {count} fois")
            
            print()
            print("📈 Répartition par statut:")
            for status, count in sorted(statuses.items()):
                emoji = "✅" if status == "SUCCESS" else "❌" if status in ["FAILURE", "ERROR"] else "⚠️"
                print(f"   • {emoji} {status}: {count} fois")
            
            print()
            print("🧠 Modèles utilisés:")
            for model, count in sorted(models.items()):
                print(f"   • {model}: {count} appel(s)")
            
            print()
            
            # Vérifier la couverture des actions
            expected_actions = {'ANALYSIS', 'FIX'}
            covered_actions = set(actions.keys()) & set(valid_actions)
            
            if expected_actions.issubset(covered_actions):
                print("✅ Couverture des actions : Minimale atteinte (ANALYSIS + FIX)")
            else:
                missing = expected_actions - covered_actions
                print(f"⚠️  Actions manquantes : {', '.join(missing)}")
                print("   Conseil : Assurez-vous que tous vos agents principaux sont actifs")
            
            print()
            print("=" * 60)
        
        return errors == 0
        
    except json.JSONDecodeError as e:
        print(f"❌ ERREUR DE PARSING JSON : {e}")
        print(f"   Ligne {e.lineno}, Colonne {e.colno}")
        print()
        print("💡 Le fichier JSON est corrompu. Vérifiez:")
        print("   • Que toutes les accolades sont bien fermées")
        print("   • Qu'il n'y a pas de virgule en trop")
        print("   • Que les chaînes sont entre guillemets")
        return False
    
    except Exception as e:
        print(f"❌ ERREUR INATTENDUE : {type(e).__name__}")
        print(f"   {str(e)}")
        return False


if __name__ == "__main__":
    success = validate_experiment_logs()
    
    # Code de sortie pour les scripts automatisés
    sys.exit(0 if success else 1)