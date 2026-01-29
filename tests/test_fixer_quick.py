"""
Test rapide de l'Agent Correcteur (Fixer)
Teste le workflow complet : Audit -> Fix
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

# Import des agents
try:
    from src.agents.auditor_agent import AuditorAgent
    from src.agents.fixer_agent import FixerAgent
    print("✅ Import des agents réussi")
except ImportError as e:
    print(f"❌ ERREUR d'import : {e}")
    sys.exit(1)


def test_fixer_quick():
    """Test rapide du Correcteur"""
    
    print("\n" + "="*80)
    print("TEST RAPIDE DU CORRECTEUR (FIXER)")
    print("="*80 + "\n")
    
    # Crée un fichier avec bugs simples
    test_code = """import os

def calculate(x, y):
    result = x / y
    return result

def process():
    print(calculate(10, 0))
    print(undefined_var)
"""
    
    # Crée le fichier de test
    os.makedirs("sandbox", exist_ok=True)
    test_file = "sandbox/test_fixer_quick.py"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"📄 Fichier de test créé : {test_file}")
    print(f"📏 Code original ({len(test_code.splitlines())} lignes) :")
    print("-"*80)
    print(test_code)
    print("-"*80)
    
    # ÉTAPE 1 : AUDIT
    print("\n" + "="*80)
    print("ÉTAPE 1 : AUDIT DU CODE")
    print("="*80)
    
    auditor = AuditorAgent()
    audit_report = auditor.analyze_file(test_file)
    
    if audit_report is None:
        print("❌ ÉCHEC : Audit échoué")
        return False
    
    bugs_found = audit_report.get('total_issues', 0)
    print(f"\n✅ Audit terminé : {bugs_found} bug(s) détecté(s)")
    
    if bugs_found == 0:
        print("⚠️ Aucun bug détecté - Test non pertinent")
        return False
    
    # ÉTAPE 2 : CORRECTION
    print("\n" + "="*80)
    print("ÉTAPE 2 : CORRECTION DU CODE")
    print("="*80)
    
    fixer = FixerAgent()
    fix_success = fixer.fix_file(test_file, audit_report)
    
    if not fix_success:
        print("\n❌ ÉCHEC : Correction échouée")
        return False
    
    print("\n✅ Correction terminée")
    
    # ÉTAPE 3 : VÉRIFICATION
    print("\n" + "="*80)
    print("ÉTAPE 3 : VÉRIFICATION DU CODE CORRIGÉ")
    print("="*80)
    
    # Lit le code corrigé
    with open(test_file, 'r', encoding='utf-8') as f:
        fixed_code = f.read()
    
    print(f"\n📏 Code corrigé ({len(fixed_code.splitlines())} lignes) :")
    print("-"*80)
    print(fixed_code[:500])  # Affiche les 500 premiers caractères
    if len(fixed_code) > 500:
        print("... (tronqué)")
    print("-"*80)
    
    # Vérifie la syntaxe
    try:
        compile(fixed_code, test_file, 'exec')
        print("\n✅ Code syntaxiquement VALIDE")
        syntax_ok = True
    except SyntaxError as e:
        print(f"\n❌ ERREUR DE SYNTAXE : {e}")
        syntax_ok = False
    
    # Vérifie les corrections
    print("\n📈 VÉRIFICATIONS :")
    
    # Vérifie import math ajouté
    has_import_math = "import math" in fixed_code
    print(f"   {'✅' if has_import_math else '❌'} Import 'math' ajouté")
    
    # Vérifie protection division par zéro
    has_check = "if" in fixed_code and ("== 0" in fixed_code or "!= 0" in fixed_code)
    print(f"   {'✅' if has_check else '⚠️'} Protection division par zéro")
    
    # Vérifie docstrings
    has_docstrings = '"""' in fixed_code or "'''" in fixed_code
    print(f"   {'✅' if has_docstrings else '❌'} Docstrings ajoutées")
    
    # Vérifie que undefined_var a été corrigé
    has_undefined = "undefined_var" in fixed_code
    print(f"   {'✅' if not has_undefined else '❌'} Variable non définie corrigée")
    
    # Vérifie les logs
    log_file = "logs/experiment_data.json"
    if os.path.exists(log_file):
        print("   ✅ Fichier de logs mis à jour")
    
    print("\n" + "="*80)
    
    # Résultat final
    all_good = syntax_ok and has_docstrings and not has_undefined
    
    if all_good:
        print("🎉 SUCCÈS : Le Correcteur fonctionne correctement !")
        print("="*80 + "\n")
        return True
    else:
        print("⚠️ PARTIEL : Le Correcteur fonctionne mais peut être amélioré")
        print("="*80 + "\n")
        return False


if __name__ == "__main__":
    try:
        success = test_fixer_quick()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)