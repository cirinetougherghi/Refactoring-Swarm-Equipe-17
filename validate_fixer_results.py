"""
Script de validation détaillée des corrections
Vérifie que le Correcteur a bien fait son travail
"""

import os
import json


def validate_correction(original_file, audit_file, fixed_file):
    """
    Valide que la correction est correcte.
    
    Args:
        original_file: Fichier original buggé
        audit_file: Rapport JSON de l'audit
        fixed_file: Fichier corrigé
    """
    print("=" * 80)
    print("🔍 VALIDATION DE LA CORRECTION")
    print("=" * 80)
    
    # Lecture des fichiers
    with open(original_file, 'r') as f:
        original_code = f.read()
    
    with open(audit_file, 'r') as f:
        audit_report = json.load(f)
    
    with open(fixed_file, 'r') as f:
        fixed_code = f.read()
    
    print(f"\n📄 Fichier original : {original_file}")
    print(f"📄 Fichier corrigé : {fixed_file}")
    print(f"🐛 Bugs détectés : {audit_report.get('total_issues', 0)}")
    
    # VÉRIFICATION 1 : Syntaxe Python valide
    print("\n" + "=" * 80)
    print("1️⃣ VÉRIFICATION SYNTAXE")
    print("=" * 80)
    
    try:
        compile(fixed_code, fixed_file, 'exec')
        print("✅ Code syntaxiquement VALIDE")
        syntax_valid = True
    except SyntaxError as e:
        print(f"❌ ERREUR DE SYNTAXE !")
        print(f"   Ligne {e.lineno}: {e.msg}")
        print(f"   {e.text}")
        syntax_valid = False
    
    # VÉRIFICATION 2 : Pas de balises markdown
    print("\n" + "=" * 80)
    print("2️⃣ VÉRIFICATION FORMAT")
    print("=" * 80)
    
    has_markdown = False
    if "```python" in fixed_code or "```" in fixed_code:
        print("❌ Le code contient des balises markdown !")
        has_markdown = True
    else:
        print("✅ Pas de balises markdown")
    
    # VÉRIFICATION 3 : Bugs critiques corrigés
    print("\n" + "=" * 80)
    print("3️⃣ VÉRIFICATION CORRECTIONS")
    print("=" * 80)
    
    corrections_ok = []
    corrections_missing = []
    
    for issue in audit_report.get('issues', []):
        issue_type = issue.get('type')
        severity = issue.get('severity')
        line = issue.get('line')
        
        if issue_type == 'missing_import':
            # Vérifie que l'import a été ajouté
            if 'import math' in fixed_code:
                print(f"✅ Ligne {line} : Import ajouté")
                corrections_ok.append(issue_type)
            else:
                print(f"❌ Ligne {line} : Import MANQUANT")
                corrections_missing.append(issue_type)
        
        elif issue_type == 'missing_docstring':
            # Vérifie qu'il y a plus de docstrings
            original_docstrings = original_code.count('"""')
            fixed_docstrings = fixed_code.count('"""')
            if fixed_docstrings > original_docstrings:
                print(f"✅ Ligne {line} : Docstring ajoutée (total: {fixed_docstrings})")
                corrections_ok.append(issue_type)
            else:
                print(f"❌ Ligne {line} : Docstring MANQUANTE")
                corrections_missing.append(issue_type)
        
        elif issue_type == 'division_by_zero':
            # Vérifie qu'une protection a été ajoutée
            if 'if' in fixed_code and ('== 0' in fixed_code or 'not' in fixed_code):
                print(f"✅ Ligne {line} : Protection ajoutée")
                corrections_ok.append(issue_type)
            else:
                print(f"⚠️  Ligne {line} : Protection division par zéro à vérifier")
        
        elif issue_type == 'pep8_spacing':
            # Difficile à vérifier automatiquement
            print(f"⚠️  Ligne {line} : Espacement PEP8 à vérifier manuellement")
        
        elif issue_type == 'undefined_variable':
            # Vérifie que la variable n'est plus utilisée sans définition
            print(f"⚠️  Ligne {line} : Variable à vérifier manuellement")
    
    # VÉRIFICATION 4 : Structure préservée
    print("\n" + "=" * 80)
    print("4️⃣ VÉRIFICATION STRUCTURE")
    print("=" * 80)
    
    # Compte les fonctions
    original_functions = original_code.count('def ')
    fixed_functions = fixed_code.count('def ')
    
    if original_functions == fixed_functions:
        print(f"✅ Nombre de fonctions préservé : {fixed_functions}")
    else:
        print(f"⚠️  Nombre de fonctions changé : {original_functions} → {fixed_functions}")
    
    # Vérifie la taille
    original_lines = len(original_code.splitlines())
    fixed_lines = len(fixed_code.splitlines())
    diff = fixed_lines - original_lines
    
    print(f"📏 Lignes originales : {original_lines}")
    print(f"📏 Lignes corrigées : {fixed_lines}")
    print(f"📏 Différence : {diff:+d} lignes")
    
    if diff > 0:
        print("   ℹ️  Code augmenté (normal avec docstrings et protections)")
    
    # RÉSUMÉ FINAL
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DE LA VALIDATION")
    print("=" * 80)
    
    score = 0
    total = 4
    
    if syntax_valid:
        score += 1
        print("✅ Syntaxe valide")
    else:
        print("❌ Syntaxe invalide")
    
    if not has_markdown:
        score += 1
        print("✅ Format pur Python")
    else:
        print("❌ Contient du markdown")
    
    if len(corrections_ok) > 0:
        score += 1
        print(f"✅ Corrections détectées ({len(corrections_ok)})")
    else:
        print("❌ Aucune correction détectée")
    
    if original_functions == fixed_functions:
        score += 1
        print("✅ Structure préservée")
    else:
        print("⚠️  Structure modifiée")
    
    print("\n" + "=" * 80)
    print(f"NOTE FINALE : {score}/{total} ({score/total*100:.0f}%)")
    print("=" * 80)
    
    if score == total:
        print("🎉 CORRECTION PARFAITE !")
    elif score >= 3:
        print("✅ Correction acceptable avec quelques améliorations possibles")
    else:
        print("⚠️  Correction nécessite des améliorations importantes")
    
    return score >= 3


def main():
    """Valide la correction de buggy_code_simple.py"""
    
    print("\n" + "🔍" * 40)
    print("VALIDATION DES RÉSULTATS DU CORRECTEUR")
    print("🔍" * 40 + "\n")
    
    validate_correction(
        "sandbox/test_samples/buggy_code_simple.py",
        "results_audit_buggy_code_simple.json",
        "results_fixed_buggy_code_simple.py"
    )
    
    print("\n✅ VALIDATION TERMINÉE !\n")


if __name__ == "__main__":
    main()