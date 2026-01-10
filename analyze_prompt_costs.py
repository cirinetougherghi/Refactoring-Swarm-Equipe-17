"""
Script d'analyse des coûts en tokens des prompts.

Ce script mesure précisément le nombre de tokens utilisés par chaque agent
et identifie les opportunités d'optimisation.

Auteur : Ingénieur Prompt
Date : 10/01/2026
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

# Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel('gemini-2.5-flash')


def count_tokens_estimate(text: str) -> int:
    """
    Estime le nombre de tokens (approximatif).
    
    Règle approximative : 1 token ≈ 4 caractères en anglais
    Pour du code Python : 1 token ≈ 3.5 caractères
    
    Args:
        text (str): Texte à analyser
    
    Returns:
        int: Nombre de tokens estimé
    """
    # Approximation simple : 1 token ≈ 4 caractères
    return len(text) // 4


def analyze_auditor_costs():
    """Analyse les coûts du prompt Auditeur."""
    
    print("\n" + "=" * 80)
    print("🔍 ANALYSE DU PROMPT AUDITEUR")
    print("=" * 80 + "\n")
    
    test_files = {
        "simple": "sandbox/test_samples/buggy_code_simple.py",
        "medium": "sandbox/test_samples/buggy_code_medium.py",
        "complex": "sandbox/test_samples/buggy_code_complex.py",
    }
    
    results = []
    
    for level, file_path in test_files.items():
        if not os.path.exists(file_path):
            print(f"⚠️  Fichier non trouvé : {file_path}")
            continue
        
        print(f"\n📄 Analyse : {level.upper()}")
        print("-" * 80)
        
        # Lit le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Génère le prompt
        filename = os.path.basename(file_path)
        prompt = get_auditor_prompt(filename, code)
        
        # Compte les tokens
        prompt_tokens = count_tokens_estimate(prompt)
        code_tokens = count_tokens_estimate(code)
        
        print(f"   Code original : {len(code)} caractères, ~{code_tokens} tokens")
        print(f"   Prompt complet : {len(prompt)} caractères, ~{prompt_tokens} tokens")
        
        # Appelle Gemini pour avoir la réponse
        try:
            response = MODEL.generate_content(prompt)
            response_tokens = count_tokens_estimate(response.text)
            print(f"   Réponse : {len(response.text)} caractères, ~{response_tokens} tokens")
            
            total = prompt_tokens + response_tokens
            print(f"   ✅ TOTAL : ~{total} tokens")
            
            results.append({
                "level": level,
                "agent": "auditor",
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
                "total_tokens": total,
            })
        except Exception as e:
            print(f"   ❌ Erreur API : {e}")
    
    return results


def analyze_fixer_costs():
    """Analyse les coûts du prompt Correcteur."""
    
    print("\n" + "=" * 80)
    print("🔧 ANALYSE DU PROMPT CORRECTEUR")
    print("=" * 80 + "\n")
    
    # Utilise buggy_code_simple avec son rapport d'audit
    file_path = "sandbox/test_samples/buggy_code_simple.py"
    
    if not os.path.exists(file_path):
        print(f"⚠️  Fichier non trouvé : {file_path}")
        return []
    
    print(f"\n📄 Analyse : SIMPLE (avec rapport d'audit)")
    print("-" * 80)
    
    # Lit le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    filename = os.path.basename(file_path)
    
    # Crée un rapport d'audit simulé
    audit_report = {
        "file": filename,
        "total_issues": 4,
        "issues": [
            {
                "line": 3,
                "type": "missing_docstring",
                "severity": "MEDIUM",
                "description": "Function missing docstring",
                "suggestion": "Add docstring"
            },
            {
                "line": 6,
                "type": "division_by_zero",
                "severity": "HIGH",
                "description": "Division by zero possible",
                "suggestion": "Add check"
            },
            {
                "line": 9,
                "type": "missing_docstring",
                "severity": "MEDIUM",
                "description": "Function missing docstring",
                "suggestion": "Add docstring"
            },
            {
                "line": 13,
                "type": "missing_import",
                "severity": "CRITICAL",
                "description": "Module math not imported",
                "suggestion": "Add import math"
            }
        ]
    }
    
    # Génère le prompt
    prompt = get_fixer_prompt(filename, code, audit_report)
    
    # Compte les tokens
    prompt_tokens = count_tokens_estimate(prompt)
    code_tokens = count_tokens_estimate(code)
    report_tokens = count_tokens_estimate(json.dumps(audit_report))
    
    print(f"   Code original : {len(code)} caractères, ~{code_tokens} tokens")
    print(f"   Rapport audit : ~{report_tokens} tokens")
    print(f"   Prompt complet : {len(prompt)} caractères, ~{prompt_tokens} tokens")
    
    # Appelle Gemini
    try:
        response = MODEL.generate_content(prompt)
        response_tokens = count_tokens_estimate(response.text)
        print(f"   Réponse : {len(response.text)} caractères, ~{response_tokens} tokens")
        
        total = prompt_tokens + response_tokens
        print(f"   ✅ TOTAL : ~{total} tokens")
        
        return [{
            "level": "simple",
            "agent": "fixer",
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total,
        }]
    except Exception as e:
        print(f"   ❌ Erreur API : {e}")
        return []


def analyze_judge_costs():
    """Analyse les coûts du prompt Testeur."""
    
    print("\n" + "=" * 80)
    print("⚖️  ANALYSE DU PROMPT TESTEUR")
    print("=" * 80 + "\n")
    
    # Pytest output simulé (succès)
    pytest_output_success = """
============================= test session starts ==============================
collected 5 items

test_example.py .....                                                    [100%]

============================== 5 passed in 0.12s ===============================
"""
    
    # Pytest output simulé (échecs)
    pytest_output_failure = """
============================= test session starts ==============================
collected 5 items

test_example.py ..F.F                                                    [ 60%]

=================================== FAILURES ===================================
________________________________ test_division _________________________________

    def test_division():
>       assert divide(10, 0) == 0
E       ZeroDivisionError: division by zero

test_example.py:15: ZeroDivisionError
=========================== short test summary info ============================
FAILED test_example.py::test_division - ZeroDivisionError: division by zero
FAILED test_example.py::test_import - ModuleNotFoundError: No module named 'math'
========================= 3 passed, 2 failed in 0.25s ==========================
"""
    
    results = []
    
    for case, pytest_output in [("success", pytest_output_success), ("failure", pytest_output_failure)]:
        print(f"\n📄 Analyse : {case.upper()}")
        print("-" * 80)
        
        # Génère le prompt
        prompt = get_judge_prompt("test_file.py", pytest_output)
        
        # Compte les tokens
        prompt_tokens = count_tokens_estimate(prompt)
        pytest_tokens = count_tokens_estimate(pytest_output)
        
        print(f"   Pytest output : {len(pytest_output)} caractères, ~{pytest_tokens} tokens")
        print(f"   Prompt complet : {len(prompt)} caractères, ~{prompt_tokens} tokens")
        
        # Appelle Gemini
        try:
            response = MODEL.generate_content(prompt)
            response_tokens = count_tokens_estimate(response.text)
            print(f"   Réponse : {len(response.text)} caractères, ~{response_tokens} tokens")
            
            total = prompt_tokens + response_tokens
            print(f"   ✅ TOTAL : ~{total} tokens")
            
            results.append({
                "level": case,
                "agent": "judge",
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
                "total_tokens": total,
            })
        except Exception as e:
            print(f"   ❌ Erreur API : {e}")
    
    return results


def print_summary(all_results):
    """Affiche le résumé global des coûts."""
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ GLOBAL DES COÛTS")
    print("=" * 80 + "\n")
    
    # Groupe par agent
    by_agent = {}
    for result in all_results:
        agent = result["agent"]
        if agent not in by_agent:
            by_agent[agent] = []
        by_agent[agent].append(result)
    
    for agent, results in by_agent.items():
        print(f"\n🔹 {agent.upper()}")
        
        avg_prompt = sum(r["prompt_tokens"] for r in results) // len(results)
        avg_response = sum(r["response_tokens"] for r in results) // len(results)
        avg_total = sum(r["total_tokens"] for r in results) // len(results)
        
        print(f"   Prompt moyen   : ~{avg_prompt} tokens")
        print(f"   Réponse moyenne : ~{avg_response} tokens")
        print(f"   Total moyen    : ~{avg_total} tokens")
        
        # Détails par niveau
        for result in results:
            print(f"      - {result['level']}: {result['total_tokens']} tokens")
    
    # Workflow complet
    auditor_avg = sum(r["total_tokens"] for r in by_agent.get("auditor", [])) // len(by_agent.get("auditor", [1]))
    fixer_avg = sum(r["total_tokens"] for r in by_agent.get("fixer", [])) // len(by_agent.get("fixer", [1]))
    judge_avg = sum(r["total_tokens"] for r in by_agent.get("judge", [])) // len(by_agent.get("judge", [1]))
    
    workflow_total = auditor_avg + fixer_avg + judge_avg
    
    print(f"\n🎯 WORKFLOW COMPLET (Audit + Fix + Judge)")
    print(f"   Total estimé : ~{workflow_total} tokens")
    print(f"   Note : Gratuit avec Gemini Flash")
    
    # Sauvegarde les résultats
    output_file = "prompt_costs_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "by_agent": by_agent,
            "workflow_total": workflow_total,
            "all_results": all_results
        }, f, indent=2)
    
    print(f"\n💾 Résultats sauvegardés : {output_file}")


def main():
    """Fonction principale."""
    
    print("\n" + "💰" * 40)
    print("ANALYSE DES COÛTS EN TOKENS - TOUS LES AGENTS")
    print("💰" * 40)
    
    all_results = []
    
    # Analyse chaque agent
    all_results.extend(analyze_auditor_costs())
    all_results.extend(analyze_fixer_costs())
    all_results.extend(analyze_judge_costs())
    
    # Résumé
    print_summary(all_results)
    
    print("\n" + "=" * 80)
    print("✅ ANALYSE TERMINÉE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
    