"""
EXEMPLE D'INTÉGRATION POUR L'ORCHESTRATEUR

Ce script montre comment utiliser les 3 agents (Auditeur, Correcteur, Testeur)
dans un workflow complet.

Destinataire : Lead Dev (Orchestrateur)
Auteur : Ingénieur Prompt
Date : 10/01/2026
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Import des fonctions de prompts
from src.prompts import (
    get_auditor_prompt,
    get_fixer_prompt,
    get_judge_prompt,
    PROMPT_VERSIONS,
    ESTIMATED_COSTS,
    print_module_info,
)

# Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel('gemini-2.5-flash')


def run_complete_workflow(file_path: str, max_iterations: int = 3):
    """
    Exécute le workflow complet : Audit -> Fix -> Test -> (repeat if needed).
    
    Args:
        file_path (str): Chemin vers le fichier Python à analyser et corriger
        max_iterations (int): Nombre maximum d'itérations (protection boucle infinie)
    
    Returns:
        dict: Résultats du workflow complet
    """
    
    print("\n" + "🔄" * 40)
    print("WORKFLOW COMPLET : AUDITEUR → CORRECTEUR → TESTEUR")
    print("🔄" * 40 + "\n")
    
    # Lecture du fichier original
    with open(file_path, 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    file_name = os.path.basename(file_path)
    current_code = original_code
    iteration = 0
    
    workflow_results = {
        "file": file_name,
        "iterations": [],
        "final_status": None,
        "total_bugs_found": 0,
        "total_bugs_fixed": 0,
    }
    
    # Boucle de feedback
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*80}")
        print(f"ITÉRATION {iteration}/{max_iterations}")
        print(f"{'='*80}\n")
        
        iteration_data = {
            "iteration": iteration,
            "audit": None,
            "fix": None,
            "test": None,
        }
        
        # ============================================================
        # ÉTAPE 1 : AUDITEUR
        # ============================================================
        print("🔍 ÉTAPE 1 : AUDIT DU CODE")
        print("-" * 80)
        
        # Génère le prompt avec la fonction helper
        audit_prompt = get_auditor_prompt(file_name, current_code)
        
        # Appelle Gemini
        audit_response = MODEL.generate_content(audit_prompt)
        audit_json_str = audit_response.text.strip()
        
        # Parse le JSON
        if audit_json_str.startswith("```json"):
            audit_json_str = audit_json_str[7:-3].strip()
        
        try:
            audit_report = json.loads(audit_json_str)
        except json.JSONDecodeError:
            print("❌ ERREUR : JSON invalide de l'Auditeur")
            workflow_results["final_status"] = "AUDIT_JSON_ERROR"
            break
        
        iteration_data["audit"] = audit_report
        
        bugs_found = audit_report.get("total_issues", 0)
        print(f"✅ Audit terminé : {bugs_found} problème(s) détecté(s)")
        
        if bugs_found == 0:
            print("✨ Code propre ! Pas de correction nécessaire.")
            workflow_results["final_status"] = "CLEAN_CODE"
            workflow_results["iterations"].append(iteration_data)
            break
        
        workflow_results["total_bugs_found"] += bugs_found
        
        # ============================================================
        # ÉTAPE 2 : CORRECTEUR
        # ============================================================
        print("\n🔧 ÉTAPE 2 : CORRECTION DU CODE")
        print("-" * 80)
        
        # Génère le prompt avec la fonction helper
        fix_prompt = get_fixer_prompt(file_name, current_code, audit_report)
        
        # Appelle Gemini
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = fix_response.text.strip()
        
        # Nettoie le code (enlève markdown si présent)
        if fixed_code.startswith("```python"):
            fixed_code = fixed_code[9:-3].strip()
        elif fixed_code.startswith("```"):
            fixed_code = fixed_code[3:-3].strip()
        
        iteration_data["fix"] = {
            "original_lines": len(current_code.splitlines()),
            "fixed_lines": len(fixed_code.splitlines()),
        }
        
        # Vérifie la syntaxe
        try:
            compile(fixed_code, file_name, 'exec')
            print("✅ Code corrigé syntaxiquement valide")
        except SyntaxError as e:
            print(f"❌ ERREUR : Code corrigé invalide : {e}")
            workflow_results["final_status"] = "SYNTAX_ERROR"
            workflow_results["iterations"].append(iteration_data)
            break
        
        current_code = fixed_code
        workflow_results["total_bugs_fixed"] += bugs_found
        
        # ============================================================
        # ÉTAPE 3 : TESTEUR (Simulé ici)
        # ============================================================
        print("\n⚖️  ÉTAPE 3 : TESTS (SIMULÉ)")
        print("-" * 80)
        
        # NOTE : Dans un vrai système, on exécuterait pytest ici
        # Pour cet exemple, on simule un succès si le code est valide
        
        simulated_pytest_output = f"""
============================= test session starts ==============================
collected 5 items

test_{file_name} .....                                              [100%]

============================== 5 passed in 0.12s ===============================
"""
        
        # Génère le prompt avec la fonction helper
        judge_prompt = get_judge_prompt(file_name, simulated_pytest_output)
        
        # Appelle Gemini
        judge_response = MODEL.generate_content(judge_prompt)
        judge_json_str = judge_response.text.strip()
        
        # Parse le JSON
        if judge_json_str.startswith("```json"):
            judge_json_str = judge_json_str[7:-3].strip()
        
        try:
            judge_report = json.loads(judge_json_str)
        except json.JSONDecodeError:
            print("❌ ERREUR : JSON invalide du Testeur")
            workflow_results["final_status"] = "JUDGE_JSON_ERROR"
            break
        
        iteration_data["test"] = judge_report
        
        decision = judge_report.get("decision", "UNKNOWN")
        print(f"✅ Décision du Testeur : {decision}")
        
        workflow_results["iterations"].append(iteration_data)
        
        if decision == "VALIDATE":
            workflow_results["final_status"] = "VALIDATED"
            print("\n🎉 CODE VALIDÉ ! Workflow terminé.")
            break
        elif decision == "PASS_TO_FIXER":
            print("\n⚠️  Tests échoués. Nouvelle itération nécessaire...")
            # Dans un vrai système, on réinjecterait les erreurs au Correcteur
            continue
    
    # Timeout
    if iteration >= max_iterations and workflow_results["final_status"] is None:
        workflow_results["final_status"] = "MAX_ITERATIONS_REACHED"
        print(f"\n⚠️  Limite de {max_iterations} itérations atteinte.")
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DU WORKFLOW")
    print("=" * 80)
    print(f"Fichier         : {file_name}")
    print(f"Itérations      : {len(workflow_results['iterations'])}")
    print(f"Bugs détectés   : {workflow_results['total_bugs_found']}")
    print(f"Bugs corrigés   : {workflow_results['total_bugs_fixed']}")
    print(f"Status final    : {workflow_results['final_status']}")
    print("=" * 80 + "\n")
    
    return workflow_results


def example_usage():
    """Exemple d'utilisation pour l'Orchestrateur."""
    
    # Affiche les infos du module
    print_module_info()
    
    # Exemple de workflow complet
    print("\n\n🎯 EXEMPLE DE WORKFLOW COMPLET\n")
    
    # Fichier de test
    test_file = "sandbox/test_samples/buggy_code_simple.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Fichier de test non trouvé : {test_file}")
        print("💡 Crée d'abord des fichiers de test dans sandbox/test_samples/")
        return
    
    # Exécute le workflow
    results = run_complete_workflow(test_file, max_iterations=3)
    
    # Sauvegarde les résultats
    output_file = "example_workflow_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Résultats sauvegardés dans : {output_file}")


# ============================================================
# GUIDE D'UTILISATION POUR L'ORCHESTRATEUR
# ============================================================

def print_integration_guide():
    """
    Affiche le guide d'intégration pour l'Orchestrateur.
    """
    
    guide = """
    
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                  GUIDE D'INTÉGRATION POUR L'ORCHESTRATEUR                  ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    📚 IMPORTS NÉCESSAIRES
    ───────────────────────────────────────────────────────────────────────────
    
    from src.prompts import get_auditor_prompt, get_fixer_prompt, get_judge_prompt
    import google.generativeai as genai
    import json
    
    
    🔧 CONFIGURATION
    ───────────────────────────────────────────────────────────────────────────
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    
    📋 WORKFLOW DE BASE (3 étapes)
    ───────────────────────────────────────────────────────────────────────────
    
    1️⃣ AUDITEUR (Détection des bugs)
    
       prompt = get_auditor_prompt(filename, code_content)
       response = model.generate_content(prompt)
       audit_report = json.loads(response.text)
       bugs_found = audit_report["total_issues"]
    
    
    2️⃣ CORRECTEUR (Correction des bugs)
    
       prompt = get_fixer_prompt(filename, code_content, audit_report)
       response = model.generate_content(prompt)
       fixed_code = response.text
    
    
    3️⃣ TESTEUR (Validation)
    
       # Exécute pytest
       import subprocess
       result = subprocess.run(['pytest', test_file], capture_output=True)
       
       prompt = get_judge_prompt(filename, result.stdout.decode())
       response = model.generate_content(prompt)
       judge_report = json.loads(response.text)
       decision = judge_report["decision"]  # "VALIDATE" ou "PASS_TO_FIXER"
    
    
    🔄 BOUCLE DE FEEDBACK
    ───────────────────────────────────────────────────────────────────────────
    
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        # 1. Audit
        audit_report = audit(code)
        if audit_report["total_issues"] == 0:
            break  # Code propre
        
        # 2. Fix
        code = fix(code, audit_report)
        
        # 3. Test
        judge_report = test(code)
        if judge_report["decision"] == "VALIDATE":
            break  # Succès !
        
        iteration += 1
    
    
    🛡️ GESTION D'ERREURS
    ───────────────────────────────────────────────────────────────────────────
    
    # Nettoyer les balises markdown dans le JSON
    response_text = response.text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:-3]
    
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Erreur JSON : {e}")
        # Logger et gérer l'erreur
    
    
    📊 LOGGING (Pour le Data Officer)
    ───────────────────────────────────────────────────────────────────────────
    
    from src.utils.logger import log_experiment, ActionType
    
    log_experiment(
        agent_name="Auditor",
        model_used="gemini-2.5-flash",
        action=ActionType.ANALYSIS,
        details={
            "file": filename,
            "input_prompt": prompt,
            "output_response": response.text,
            "bugs_found": audit_report["total_issues"]
        },
        status="SUCCESS"
    )
    
    
    💰 ESTIMATIONS DE COÛTS
    ───────────────────────────────────────────────────────────────────────────
    
    from src.prompts import ESTIMATED_COSTS
    
    # Workflow complet : ~9050 tokens (~12 secondes)
    total_cost = ESTIMATED_COSTS["total_workflow"]["total_tokens_avg"]
    
    
    ✅ POINTS D'ATTENTION
    ───────────────────────────────────────────────────────────────────────────
    
    ⚠️  Toujours nettoyer les réponses JSON (enlever ```json si présent)
    ⚠️  Limiter les itérations (max 10) pour éviter les boucles infinies
    ⚠️  Logger chaque interaction avec les agents
    ⚠️  Vérifier la syntaxe du code corrigé avec compile()
    ⚠️  Gérer les cas où pytest plante
    
    
    
    """
    
    print(guide)


if __name__ == "__main__":
    # Affiche le guide
    print_integration_guide()
    
    # Lance l'exemple
    print("\n\n" + "🚀" * 40)
    print("LANCEMENT DE L'EXEMPLE")
    print("🚀" * 40 + "\n")
    
    example_usage()