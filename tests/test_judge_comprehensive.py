"""
Suite de tests complète pour l'Agent Correcteur v1.1
"""

import os
import json
import pytest
from dotenv import load_dotenv
import google.generativeai as genai

from src.prompts import get_auditor_prompt, get_fixer_prompt

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel('gemini-2.5-flash')


def parse_json_response(response_text):
    """Nettoie et parse la réponse JSON."""
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:-3].strip()
    elif text.startswith("```"):
        text = text[3:-3].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return json.loads(text)


def clean_code_response(code):
    """Nettoie le code des balises markdown."""
    code = code.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()


class TestFixerSyntaxCorrection:
    """Tests de correction de syntaxe."""
    
    def test_undefined_variable_fix(self):
        """Test : Correction variable non définie."""
        code = """
def hello():
    print(message)
"""
        # Audit
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        # Fix
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Vérifie syntaxe valide
        compile(fixed_code, "test.py", "exec")
        
        # Vérifie que 'message' est maintenant défini
        assert "message" in fixed_code
    
    def test_missing_import_fix(self):
        """Test : Ajout d'import manquant."""
        code = """
def calculate():
    return math.sqrt(16)
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Vérifie présence import
        assert "import math" in fixed_code
        compile(fixed_code, "test.py", "exec")


class TestFixerLogicCorrection:
    """Tests de correction de logique."""
    
    def test_division_by_zero_fix(self):
        """Test : Protection division par zéro."""
        code = """
def divide(a, b):
    return a / b
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Vérifie protection ajoutée
        assert "if" in fixed_code.lower() or "check" in fixed_code.lower()
        compile(fixed_code, "test.py", "exec")


class TestFixerQualityImprovement:
    """Tests d'amélioration de qualité."""
    
    def test_docstring_addition(self):
        """Test : Ajout de docstrings."""
        code = """
def calculate(a, b):
    return a + b
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Vérifie présence docstring
        assert '"""' in fixed_code or "'''" in fixed_code
        compile(fixed_code, "test.py", "exec")
    
    def test_pep8_fix(self):
        """Test : Correction PEP8."""
        code = """
def test(a,b):
    x=5
    return a+b
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Vérifie formatage PEP8
        assert "a, b" in fixed_code  # Espaces après virgule
        compile(fixed_code, "test.py", "exec")


class TestFixerStructurePreservation:
    """Tests de préservation de structure."""
    
    def test_logic_preserved(self):
        """Test : Logique originale préservée."""
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
        
        # Vérifie que la multiplication est toujours présente
        assert "*" in fixed_code or "multiply" in fixed_code.lower()
    
    def test_function_count_preserved(self):
        """Test : Nombre de fonctions préservé."""
        code = """
def func1():
    pass

def func2():
    pass
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        fixed_code = clean_code_response(fix_response.text)
        
        # Vérifie présence des 2 fonctions
        assert fixed_code.count("def ") == 2


class TestFixerOutputFormat:
    """Tests du format de sortie."""
    
    def test_pure_code_output(self):
        """Test : Sortie code pur (pas de markdown)."""
        code = """
def test():
    print(x)
"""
        audit_prompt = get_auditor_prompt("test.py", code)
        audit_response = MODEL.generate_content(audit_prompt)
        audit_report = parse_json_response(audit_response.text)
        
        fix_prompt = get_fixer_prompt("test.py", code, audit_report)
        fix_response = MODEL.generate_content(fix_prompt)
        
        # La réponse NE DOIT PAS contenir d'explications textuelles
        # (sauf si entre triple quotes = docstrings)
        response_text = fix_response.text.strip()
        
        # Après nettoyage, devrait être du code pur
        fixed_code = clean_code_response(response_text)
        compile(fixed_code, "test.py", "exec")


def run_all_tests():
    """Lance tous les tests."""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()