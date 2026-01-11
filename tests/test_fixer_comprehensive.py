"""
Suite de tests complète pour l'Agent Correcteur

Tests :
- Corrige les variables non définies
- Ajoute les docstrings
- Produit du code Python valide
- Ne modifie pas trop le code original
"""

import os
import json
import pytest
from dotenv import load_dotenv
import google.generativeai as genai

from src.prompts.auditor_prompt import get_auditor_prompt
from src.prompts.fixer_prompt import get_fixer_prompt

# Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel('gemini-2.5-flash')


def parse_json_response(response_text):
    """Parse le JSON de l'audit."""
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    if not text.startswith("{"):
        start = text.find("{")
        if start != -1:
            text = text[start:]
    if not text.endswith("}"):
        end = text.rfind("}")
        if end != -1:
            text = text[:end+1]
    
    return json.loads(text)


def clean_code_response(response_text):
    """Nettoie le code des balises markdown."""
    text = response_text.strip()
    
    if text.startswith("```python"):
        text = text[9:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]
    
    return text.strip()


class TestFixerVariableCorrection:
    """Tests de correction des variables non définies."""
    
    def test_fix_undefined_variable(self):
        """Le Correcteur DOIT corriger une variable non définie."""
        code = """
def hello():
    print(message)

hello()
"""
        # Étape 1 : Audit
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        # Étape 2 : Correction
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Vérifie que le code est valide Python
        try:
            compile(fixed_code, "test.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Code corrigé invalide: {e}\n{fixed_code}")
        
        # Vérifie que 'message' est maintenant défini
        assert "message" in fixed_code, "La variable 'message' devrait être définie"
    
    def test_fix_undefined_function(self):
        """Le Correcteur DOIT corriger/importer une fonction non définie."""
        code = """
def calculate():
    result = sqrt(16)
    return result
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Vérifie syntaxe valide
        compile(fixed_code, "test.py", "exec")
        
        # Vérifie import math ajouté OU fonction sqrt définie
        assert ("import math" in fixed_code or "def sqrt" in fixed_code), \
            "Devrait importer math ou définir sqrt"


class TestFixerDocstringAddition:
    """Tests d'ajout de docstrings."""
    
    def test_add_docstring(self):
        """Le Correcteur DOIT ajouter des docstrings manquantes."""
        code = """
def calculate(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Vérifie syntaxe valide
        compile(fixed_code, "test.py", "exec")
        
        # Vérifie présence de docstrings (""" ou ''')
        docstring_count = fixed_code.count('"""') + fixed_code.count("'''")
        assert docstring_count >= 4, "Devrait avoir au moins 2 docstrings (4 triple-quotes)"


class TestFixerCodeValidity:
    """Tests de validité du code produit."""
    
    def test_produces_valid_python(self):
        """Le code corrigé DOIT TOUJOURS être du Python valide."""
        test_cases = [
            "def f(): print(x)",
            "result = 100 / 0",
            "import os\nprint(data)",
        ]
        
        for code in test_cases:
            audit_prompt = get_auditor_prompt("test.py", code)
            audit_response = MODEL.generate_content(audit_prompt)
            audit_report = parse_json_response(audit_response.text)
            
            fix_prompt = get_fixer_prompt("test.py", code, audit_report)
            fix_response = MODEL.generate_content(fix_prompt)
            fixed_code = clean_code_response(fix_response.text)
            
            try:
                compile(fixed_code, "test.py", "exec")
            except SyntaxError as e:
                pytest.fail(f"Code invalide produit pour: {code}\nErreur: {e}\n{fixed_code}")
    
    def test_no_explanatory_text(self):
        """Le Correcteur NE DOIT PAS ajouter d'explications textuelles."""
        code = """
def test():
    print(undefined_var)
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        
        raw_response = fix_response.text.strip()
        
        # Après nettoyage des balises markdown, devrait être du code pur
        fixed_code = clean_code_response(raw_response)
        
        # Le code doit compiler
        compile(fixed_code, "test.py", "exec")
        
        # Aucune phrase explicative ne devrait rester (hors docstrings)
        # On teste que le nettoyage a bien fonctionné
        assert not raw_response.startswith("Voici"), "Ne doit pas commencer par du texte explicatif"
        assert not raw_response.startswith("Here"), "Ne doit pas commencer par du texte explicatif"


class TestFixerStructurePreservation:
    """Tests de préservation de la structure originale."""
    
    def test_logic_preserved(self):
        """La logique originale DOIT être préservée."""
        code = """
def multiply(a, b):
    return a * b
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # La multiplication doit toujours être présente
        assert "*" in fixed_code, "L'opération de multiplication doit être préservée"
        assert "def multiply" in fixed_code, "Le nom de fonction doit être préservé"
    
    def test_function_count_preserved(self):
        """Le nombre de fonctions DOIT être préservé."""
        code = """
def func1():
    pass

def func2():
    pass

def func3():
    pass
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Devrait toujours avoir 3 fonctions
        function_count = fixed_code.count("def ")
        assert function_count == 3, f"Devrait avoir 3 fonctions, trouvé {function_count}"
    
    def test_no_complete_rewrite(self):
        """Le code NE DOIT PAS être complètement réécrit."""
        code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_response.text)
        fixed_code = clean_code_response(fix_response.text)
        
        # La boucle for doit être préservée (pas remplacée par sum())
        assert "for" in fixed_code, "La boucle for doit être préservée"
        assert "total" in fixed_code, "Les variables originales doivent être préservées"


def run_all_tests():
    """Lance tous les tests."""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
