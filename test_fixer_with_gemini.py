"""
Script de test pour l'Agent Correcteur (Fixer)
Test du workflow complet : Auditeur → Correcteur
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from src.prompts.auditor_prompt import get_auditor_prompt
from src.prompts.fixer_prompt import get_fixer_prompt
# ✅ AJOUT DATA OFFICER : Import du système de logging
from src.utils.logger import log_experiment, ActionType

# Charge les variables d'environnement
load_dotenv()

# Configure l'API Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERREUR : Clé API non trouvée dans .env")
    exit(1)

genai.configure(api_key=api_key)


def test_full_workflow(file_path: str):
    """
    Teste le workflow complet sur un fichier.
    
    Workflow :
    1. Lit le fichier buggé
    2. Auditeur analyse et produit un rapport JSON
    3. Correcteur corrige le code selon le rapport
    4. Compare avant/après
    
    Args:
        file_path (str): Chemin vers le fichier à traiter
    """
    print("=" * 80)
    print(f"🔍 TEST WORKFLOW COMPLET SUR : {file_path}")
    print("=" * 80)
    
    # ========================================================================
    # ÉTAPE 1 : LECTURE DU FICHIER
    # ========================================================================
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            buggy_code = f.read()
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {file_path}")
        return
    
    file_name = os.path.basename(file_path)
    print(f"\n📄 Fichier : {file_name}")
    print(f"📏 Lignes de code original : {len(buggy_code.splitlines())}")
    
    # ========================================================================
    # ÉTAPE 2 : AUDIT (AUDITEUR)
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("🔍 ÉTAPE 1 : AUDIT DU CODE")
    print("=" * 80)
    
    # Génère le prompt de l'Auditeur
    audit_prompt = get_auditor_prompt(file_name, buggy_code)
    print(f"⚙️  Prompt Auditeur généré ({len(audit_prompt)} caractères)")
    
    # Envoie à Gemini
    print("🤖 Envoi à Gemini pour audit...")
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        audit_response = model.generate_content(audit_prompt)
        audit_raw = audit_response.text
        print(f"✅ Rapport d'audit reçu ({len(audit_raw)} caractères)")
         # ✅ AJOUT DATA OFFICER : Log de l'audit
        log_experiment(
            agent_name="Auditor_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.ANALYSIS,
            details={
                "file_analyzed": file_name,
                "input_prompt": audit_prompt,
                "output_response": audit_raw,
                "prompt_length_chars": len(audit_prompt),
                "response_length_chars": len(audit_raw)
            },
            status="SUCCESS"
        )

    except Exception as e:
        print(f"❌ Erreur lors de l'audit : {e}")
        # ✅ AJOUT DATA OFFICER : Log de l'erreur audit
        log_experiment(
            agent_name="Auditor_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.ANALYSIS,
            details={
                "file_analyzed": file_name,
                "input_prompt": audit_prompt,
                "output_response": "",
                "error_type": type(e).__name__,
                "error_message": str(e)
            },
            status="ERROR"
        )

        return
    
    # Parse le JSON
    try:
        # Nettoie la réponse
        cleaned = audit_raw.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        audit_report = json.loads(cleaned)
        print(f"✅ Rapport JSON valide")
        print(f"📊 Problèmes détectés : {audit_report.get('total_issues', 0)}")
        
        # Affiche les problèmes
        if audit_report.get('issues'):
            print("\n🐛 BUGS DÉTECTÉS :")
            for i, issue in enumerate(audit_report['issues'][:5], 1):  # Affiche max 5
                print(f"   [{i}] Ligne {issue.get('line')} - {issue.get('severity')}")
                print(f"       {issue.get('type')}: {issue.get('description')}")
            
            if len(audit_report['issues']) > 5:
                print(f"   ... et {len(audit_report['issues']) - 5} autres problèmes")
        
    except json.JSONDecodeError as e:
        print(f"❌ ERREUR : JSON invalide du rapport d'audit")
        print(f"   {e}")
        # Sauvegarde pour debug
        with open(f"debug_audit_{file_name}.txt", 'w') as f:
            f.write(audit_raw)
        print(f"💾 Réponse brute sauvegardée dans debug_audit_{file_name}.txt")
        return
    
    # ========================================================================
    # ÉTAPE 3 : CORRECTION (CORRECTEUR)
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("🔧 ÉTAPE 2 : CORRECTION DU CODE")
    print("=" * 80)
    
    # Génère le prompt du Correcteur
    fixer_prompt = get_fixer_prompt(file_name, buggy_code, audit_report)
    print(f"⚙️  Prompt Correcteur généré ({len(fixer_prompt)} caractères)")
    
    # Envoie à Gemini
    print("🤖 Envoi à Gemini pour correction...")
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        fixer_response = model.generate_content(fixer_prompt)
        fixed_code = fixer_response.text
        print(f"✅ Code corrigé reçu ({len(fixed_code)} caractères)")
         # ✅ AJOUT DATA OFFICER : Log de la correction
        log_experiment(
            agent_name="Fixer_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.FIX,
            details={
                "file_fixed": file_name,
                "input_prompt": fixer_prompt,
                "output_response": fixed_code,
                "prompt_length_chars": len(fixer_prompt),
                "response_length_chars": len(fixed_code),
                "issues_to_fix": audit_report.get('total_issues', 0)
            },
            status="SUCCESS"
        )
    except Exception as e:
        print(f"❌ Erreur lors de la correction : {e}")
         # ✅ AJOUT DATA OFFICER : Log de l'erreur correction
        log_experiment(
            agent_name="Fixer_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.FIX,
            details={
                "file_fixed": file_name,
                "input_prompt": fixer_prompt,
                "output_response": "",
                "error_type": type(e).__name__,
                "error_message": str(e)
            },
            status="ERROR"
        )
        return
    
    # Nettoie le code (enlève les balises markdown si présentes)
    cleaned_code = fixed_code.strip()
    if cleaned_code.startswith("```python"):
        cleaned_code = cleaned_code[9:]
    if cleaned_code.startswith("```"):
        cleaned_code = cleaned_code[3:]
    if cleaned_code.endswith("```"):
        cleaned_code = cleaned_code[:-3]
    cleaned_code = cleaned_code.strip()
    
    print(f"📏 Lignes de code corrigé : {len(cleaned_code.splitlines())}")
    
    # ========================================================================
    # ÉTAPE 4 : COMPARAISON & RÉSULTATS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("📊 COMPARAISON AVANT/APRÈS")
    print("=" * 80)
    
    print(f"\n📄 CODE ORIGINAL ({len(buggy_code.splitlines())} lignes) :")
    print("-" * 80)
    print(buggy_code[:500])  # Affiche les 500 premiers caractères
    if len(buggy_code) > 500:
        print("... (tronqué)")
    
    print(f"\n📄 CODE CORRIGÉ ({len(cleaned_code.splitlines())} lignes) :")
    print("-" * 80)
    print(cleaned_code[:500])  # Affiche les 500 premiers caractères
    if len(cleaned_code) > 500:
        print("... (tronqué)")
    
    # ========================================================================
    # ÉTAPE 5 : VÉRIFICATION SYNTAXIQUE
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("🔍 VÉRIFICATION DU CODE CORRIGÉ")
    print("=" * 80)
    
    # Teste si le code est syntaxiquement valide
    try:
        compile(cleaned_code, file_name, 'exec')
        print("✅ Code syntaxiquement VALIDE !")
    except SyntaxError as e:
        print(f"❌ ERREUR DE SYNTAXE dans le code corrigé !")
        print(f"   Ligne {e.lineno}: {e.msg}")
        print(f"   {e.text}")
    
    # ========================================================================
    # ÉTAPE 6 : SAUVEGARDE DES RÉSULTATS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("💾 SAUVEGARDE DES RÉSULTATS")
    print("=" * 80)
    
    # Sauvegarde le rapport d'audit
    audit_file = f"results_audit_{file_name.replace('.py', '')}.json"
    with open(audit_file, 'w', encoding='utf-8') as f:
        json.dump(audit_report, f, indent=2, ensure_ascii=False)
    print(f"✅ Rapport d'audit : {audit_file}")
    
    # Sauvegarde le code corrigé
    fixed_file = f"results_fixed_{file_name}"
    with open(fixed_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_code)
    print(f"✅ Code corrigé : {fixed_file}")
    
    # Sauvegarde une comparaison
    comparison_file = f"results_comparison_{file_name.replace('.py', '')}.txt"
    with open(comparison_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("COMPARAISON AVANT/APRÈS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Fichier : {file_name}\n")
        f.write(f"Problèmes détectés : {audit_report.get('total_issues', 0)}\n")
        f.write(f"Lignes originales : {len(buggy_code.splitlines())}\n")
        f.write(f"Lignes corrigées : {len(cleaned_code.splitlines())}\n\n")
        f.write("=" * 80 + "\n")
        f.write("CODE ORIGINAL\n")
        f.write("=" * 80 + "\n")
        f.write(buggy_code)
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("CODE CORRIGÉ\n")
        f.write("=" * 80 + "\n")
        f.write(cleaned_code)
    print(f"✅ Comparaison : {comparison_file}")
    
    print("\n" + "=" * 80)
    print("✅ TEST TERMINÉ !")
    print("=" * 80 + "\n")


def main():
    """Fonction principale - teste le workflow sur un fichier"""
    
    print("\n" + "🔧" * 40)
    print("TEST WORKFLOW COMPLET : AUDITEUR → CORRECTEUR")
    print("🔧" * 40 + "\n")
    
    # Fichier à tester (commence par le simple)
    test_file = "sandbox/test_samples/buggy_code_simple.py"
    
    print(f"📂 Fichier de test : {test_file}\n")
    
    test_full_workflow(test_file)
    
    print("\n✅ TOUS LES TESTS TERMINÉS !\n")
    print("\n📊 Les logs d'expérimentation ont été enregistrés dans logs/experiment_data.json")
    print("💡 Lancez 'python validate_logs.py' pour valider le format des logs\n")


if __name__ == "__main__":
    main()