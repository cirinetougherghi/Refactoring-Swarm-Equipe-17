"""
Test rapide de l'Agent Auditeur
Verifie que l'agent fonctionne correctement
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Configuration
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERREUR : Clé API non trouvée dans .env")
    sys.exit(1)

genai.configure(api_key=api_key)

# Import de l'agent
try:
    from src.agents.auditor_agent import AuditorAgent
    print("✅ Import de l'Agent Auditeur réussi")
except ImportError as e:
    print(f"❌ ERREUR d'import : {e}")
    sys.exit(1)


def test_quick():
    """Test rapide sur un fichier simple"""
    
    print("\n" + "="*80)
    print("TEST RAPIDE DE L'AUDITEUR")
    print("="*80 + "\n")
    
    # Crée un fichier de test simple avec des bugs évidents
    test_code = """import os

def calculate(x, y):
    result = x / y
    return result

print(calculate(10, 0))
print(undefined_variable)
"""
    
    # Crée le dossier sandbox s'il n'existe pas
    os.makedirs("sandbox", exist_ok=True)
    
    test_file = "sandbox/test_quick.py"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"📄 Fichier de test créé : {test_file}")
    print(f"📏 Code de test ({len(test_code.splitlines())} lignes) :")
    print("-"*80)
    print(test_code)
    print("-"*80)
    
    # Teste l'auditeur
    print("\n🤖 Lancement de l'Auditeur...\n")
    
    auditor = AuditorAgent()
    report = auditor.analyze_file(test_file)
    
    # Vérifications
    print("\n" + "="*80)
    print("📊 RÉSULTATS")
    print("="*80)
    
    if report is None:
        print("❌ ÉCHEC : Aucun rapport retourné")
        print("   Vérifiez les erreurs ci-dessus")
        return False
    
    print("✅ Rapport JSON reçu\n")
    
    bugs_found = report.get('total_issues', 0)
    print(f"🐛 Bugs détectés : {bugs_found}")
    
    if bugs_found == 0:
        print("⚠️  ATTENTION : Aucun bug détecté alors que le code en contient")
        return False
    
    # Affiche les bugs
    print("\n📋 Détails des problèmes :")
    for i, issue in enumerate(report.get('issues', []), 1):
        print(f"\n   [{i}] Ligne {issue.get('line', '?')}")
        print(f"       Type      : {issue.get('type', 'N/A')}")
        print(f"       Sévérité  : {issue.get('severity', 'N/A')}")
        print(f"       Description : {issue.get('description', 'N/A')}")
    
    print("\n" + "="*80)
    
    # Vérifie que les bugs critiques sont détectés
    issues = report.get('issues', [])
    
    has_division = any('division' in i.get('description', '').lower() or 
                       'division' in i.get('type', '').lower() 
                       for i in issues)
    
    has_undefined = any('undefined' in i.get('description', '').lower() or 
                        'undefined' in i.get('type', '').lower()
                        for i in issues)
    
    print("📈 VÉRIFICATIONS :")
    
    if has_division:
        print("   ✅ Division par zéro détectée")
    else:
        print("   ❌ Division par zéro NON détectée")
    
    if has_undefined:
        print("   ✅ Variable non définie détectée")
    else:
        print("   ❌ Variable non définie NON détectée")
    
    # Vérifie les logs
    log_file = "logs/experiment_data.json"
    if os.path.exists(log_file):
        print("   ✅ Fichier de logs créé")
    else:
        print("   ⚠️  Fichier de logs non trouvé")
    
    print("\n" + "="*80)
    
    if has_division and has_undefined:
        print("🎉 SUCCÈS : L'Auditeur fonctionne correctement !")
        print("="*80 + "\n")
        return True
    else:
        print("⚠️  PARTIEL : L'Auditeur fonctionne mais manque certains bugs")
        print("="*80 + "\n")
        return False


if __name__ == "__main__":
    try:
        success = test_quick()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)