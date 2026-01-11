"""
Script de comparaison v1.0 vs v1.1

Compare la qualité et les coûts entre les versions.
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

from src.prompts import (
    get_auditor_prompt,
    get_fixer_prompt,
    get_judge_prompt,
)

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel('gemini-2.5-flash')


def count_tokens(text):
    """Estime les tokens."""
    return len(text) // 4


def test_auditor_quality():
    """Teste la qualité de l'Auditeur v1.1."""
    
    print("\n" + "=" * 80)
    print("🔍 TEST AUDITEUR v1.1 - QUALITÉ")
    print("=" * 80 + "\n")
    
    test_file = "sandbox/test_samples/buggy_code_simple.py"
    
    with open(test_file, 'r') as f:
        code = f.read()
    
    filename = os.path.basename(test_file)
    
    # v1.1
    prompt = get_auditor_prompt(filename, code)
    prompt_tokens = count_tokens(prompt)
    
    print(f"📊 Prompt v1.1 : ~{prompt_tokens} tokens")
    
    response = MODEL.generate_content(prompt)
    response_text = response.text.strip()
    
    # Parse JSON
    if response_text.startswith("```json"):
        response_text = response_text[7:-3].strip()
    
    audit_report = json.loads(response_text)
    bugs_found = audit_report.get("total_issues", 0)
    
    response_tokens = count_tokens(response.text)
    total_tokens = prompt_tokens + response_tokens
    
    print(f"📊 Réponse : ~{response_tokens} tokens")
    print(f"📊 Total : ~{total_tokens} tokens")
    print(f"🐛 Bugs détectés : {bugs_found}")
    print(f"✅ JSON valide : Oui")
    
    # Attendu : 4-5 bugs
    if bugs_found >= 4:
        print(f"✅ QUALITÉ : Maintenue (attendu ≥4, obtenu {bugs_found})")
        quality_ok = True
    else:
        print(f"❌ QUALITÉ : Dégradée (attendu ≥4, obtenu {bugs_found})")
        quality_ok = False
    
    return {
        "agent": "auditor",
        "version": "1.1",
        "tokens": total_tokens,
        "bugs_found": bugs_found,
        "quality_ok": quality_ok
    }


def test_fixer_quality():
    """Teste la qualité du Correcteur v1.1."""
    
    print("\n" + "=" * 80)
    print("🔧 TEST CORRECTEUR v1.1 - QUALITÉ")
    print("=" * 80 + "\n")
    
    test_file = "sandbox/test_samples/buggy_code_simple.py"
    
    with open(test_file, 'r') as f:
        code = f.read()
    
    filename = os.path.basename(test_file)
    
    # Audit d'abord
    audit_prompt = get_auditor_prompt(filename, code)
    audit_response = MODEL.generate_content(audit_prompt)
    audit_text = audit_response.text.strip()
    if audit_text.startswith("```json"):
        audit_text = audit_text[7:-3].strip()
    audit_report = json.loads(audit_text)
    
    # Fix
    fix_prompt = get_fixer_prompt(filename, code, audit_report)
    prompt_tokens = count_tokens(fix_prompt)
    
    print(f"📊 Prompt v1.1 : ~{prompt_tokens} tokens")
    
    fix_response = MODEL.generate_content(fix_prompt)
    fixed_code = fix_response.text.strip()
    
    # Nettoie markdown
    if fixed_code.startswith("```python"):
        fixed_code = fixed_code[9:-3].strip()
    elif fixed_code.startswith("```"):
        fixed_code = fixed_code[3:-3].strip()
    
    response_tokens = count_tokens(fix_response.text)
    total_tokens = prompt_tokens + response_tokens
    
    print(f"📊 Réponse : ~{response_tokens} tokens")
    print(f"📊 Total : ~{total_tokens} tokens")
    
    # Vérifie syntaxe
    try:
        compile(fixed_code, filename, 'exec')
        syntax_ok = True
        print(f"✅ Syntaxe : Valide")
    except SyntaxError as e:
        syntax_ok = False
        print(f"❌ Syntaxe : Invalide - {e}")
    
    # Vérifie présence docstrings
    has_docstrings = '"""' in fixed_code or "'''" in fixed_code
    print(f"✅ Docstrings : {'Présentes' if has_docstrings else 'Absentes'}")
    
    quality_ok = syntax_ok and has_docstrings
    
    if quality_ok:
        print(f"✅ QUALITÉ : Maintenue")
    else:
        print(f"❌ QUALITÉ : Dégradée")
    
    return {
        "agent": "fixer",
        "version": "1.1",
        "tokens": total_tokens,
        "syntax_ok": syntax_ok,
        "has_docstrings": has_docstrings,
        "quality_ok": quality_ok
    }


def test_judge_quality():
    """Teste la qualité du Testeur v1.1."""
    
    print("\n" + "=" * 80)
    print("⚖️  TEST TESTEUR v1.1 - QUALITÉ")
    print("=" * 80 + "\n")
    
    pytest_output = """
============================= test session starts ==============================
collected 5 items

test_example.py .....                                                    [100%]

============================== 5 passed in 0.12s ===============================
"""
    
    prompt = get_judge_prompt("test_file.py", pytest_output)
    prompt_tokens = count_tokens(prompt)
    
    print(f"📊 Prompt v1.1 : ~{prompt_tokens} tokens")
    
    response = MODEL.generate_content(prompt)
    response_text = response.text.strip()
    
    if response_text.startswith("```json"):
        response_text = response_text[7:-3].strip()
    
    judge_report = json.loads(response_text)
    decision = judge_report.get("decision", "UNKNOWN")
    
    response_tokens = count_tokens(response.text)
    total_tokens = prompt_tokens + response_tokens
    
    print(f"📊 Réponse : ~{response_tokens} tokens")
    print(f"📊 Total : ~{total_tokens} tokens")
    print(f"⚖️  Décision : {decision}")
    
    # Attendu : VALIDATE (tous les tests passent)
    quality_ok = decision == "VALIDATE"
    
    if quality_ok:
        print(f"✅ QUALITÉ : Maintenue (décision correcte)")
    else:
        print(f"❌ QUALITÉ : Dégradée (décision incorrecte)")
    
    return {
        "agent": "judge",
        "version": "1.1",
        "tokens": total_tokens,
        "decision": decision,
        "quality_ok": quality_ok
    }


def main():
    """Teste toutes les versions optimisées."""
    
    print("\n" + "🔬" * 40)
    print("COMPARAISON v1.0 vs v1.1")
    print("🔬" * 40)
    
    results = []
    
    # Teste chaque agent
    results.append(test_auditor_quality())
    results.append(test_fixer_quality())
    results.append(test_judge_quality())
    
    # Résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ COMPARATIF")
    print("=" * 80 + "\n")
    
    # v1.0 (from previous analysis)
    v1_0_costs = {
        "auditor": 2259,
        "fixer": 1450,
        "judge": 1821,
        "total": 5530
    }
    
    print("💰 COÛTS (tokens) :")
    print(f"\n{'Agent':<12} {'v1.0':<10} {'v1.1':<10} {'Gain':<10} {'%':<10}")
    print("-" * 50)
    
    total_v1_1 = 0
    for r in results:
        agent = r["agent"]
        v1_0 = v1_0_costs[agent]
        v1_1 = r["tokens"]
        gain = v1_0 - v1_1
        percent = (gain / v1_0) * 100
        total_v1_1 += v1_1
        
        print(f"{agent:<12} {v1_0:<10} {v1_1:<10} {gain:<10} {percent:.1f}%")
    
    total_gain = v1_0_costs["total"] - total_v1_1
    total_percent = (total_gain / v1_0_costs["total"]) * 100
    
    print("-" * 50)
    print(f"{'WORKFLOW':<12} {v1_0_costs['total']:<10} {total_v1_1:<10} {total_gain:<10} {total_percent:.1f}%")
    
    print(f"\n✅ QUALITÉ :")
    all_ok = all(r["quality_ok"] for r in results)
    
    for r in results:
        status = "✅ OK" if r["quality_ok"] else "❌ DÉGRADÉE"
        print(f"   {r['agent']:<12} : {status}")
    
    print(f"\n{'='*80}")
    if all_ok and total_percent > 0:
        print(f"🎉 SUCCÈS ! Optimisation réussie : -{total_percent:.1f}% tokens, qualité maintenue")
    elif all_ok:
        print(f"✅ Qualité maintenue mais gain insuffisant ({total_percent:.1f}%)")
    else:
        print(f"❌ ÉCHEC : Qualité dégradée, rollback nécessaire")
    print(f"{'='*80}\n")
    
    # Sauvegarde
    with open("v1_1_comparison_results.json", 'w') as f:
        json.dump({
            "v1_0_costs": v1_0_costs,
            "v1_1_results": results,
            "total_v1_1": total_v1_1,
            "gain_tokens": total_gain,
            "gain_percent": total_percent,
            "quality_maintained": all_ok
        }, f, indent=2)
    
    print("💾 Résultats sauvegardés : v1_1_comparison_results.json\n")


if __name__ == "__main__":
    main()
    
    