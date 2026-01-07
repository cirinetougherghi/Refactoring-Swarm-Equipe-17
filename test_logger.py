from src.utils.logger import log_experiment, ActionType

# Test 1 : Log simple ANALYSIS
print("🧪 Test 1 : Log ANALYSIS...")
try:
    log_experiment(
        agent_name="Test_Agent",
        model_used="gemini-2.5-flash",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": "Ceci est un test d'analyse",
            "output_response": "Réponse de test pour l'analyse",
            "file_analyzed": "test.py"
        },
        status="SUCCESS"
    )
    print("✅ Test 1 réussi : Log ANALYSIS créé")
except Exception as e:
    print(f"❌ Test 1 échoué : {e}")

# Test 2 : Log FIX
print("\n🧪 Test 2 : Log FIX...")
try:
    log_experiment(
        agent_name="Fixer_Agent",
        model_used="gemini-2.5-flash",
        action=ActionType.FIX,
        details={
            "input_prompt": "Corrige cette fonction",
            "output_response": "Fonction corrigée avec succès",
            "file_fixed": "bug_simple.py"
        },
        status="SUCCESS"
    )
    print("✅ Test 2 réussi : Log FIX créé")
except Exception as e:
    print(f"❌ Test 2 échoué : {e}")

# Test 3 : Vérifie que l'erreur se déclenche si champs manquants
print("\n🧪 Test 3 : Validation des champs obligatoires...")
try:
    log_experiment(
        agent_name="Test_Agent",
        model_used="gemini-2.5-flash",
        action=ActionType.FIX,
        details={"file": "test.py"},  # Manque input_prompt et output_response
        status="SUCCESS"
    )
    print("❌ Test 3 échoué : L'erreur aurait dû être déclenchée")
except ValueError as e:
    print(f"✅ Test 3 réussi : Erreur détectée comme prévu")
    print(f"   Message : {e}")

# Test 4 : Vérifier le fichier JSON
print("\n🧪 Test 4 : Vérification du fichier JSON...")
import json
import os

LOG_FILE = "logs/experiment_data.json"
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Test 4 réussi : {len(data)} entrées dans le log")
    print(f"   Dernière entrée : Agent={data[-1]['agent']}, Action={data[-1]['action']}")
else:
    print(f"❌ Test 4 échoué : Fichier {LOG_FILE} introuvable")

print("\n" + "="*50)
print("📊 RÉSUMÉ DES TESTS")
print("="*50)
print("✅ Si tous les tests sont verts, le logger fonctionne parfaitement !")