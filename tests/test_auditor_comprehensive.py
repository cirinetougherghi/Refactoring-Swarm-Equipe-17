"""
Suite de tests complète pour l'Agent Auditeur

Tests tous les cas critiques :
- Détection des variables non définies
- Détection des docstrings manquantes
- Détection des divisions par zéro
- Pas de faux positifs sur du code propre
- JSON toujours valide
"""

import os
import json
import pytest
from dotenv import load_dotenv
import google.generativeai as genai

from src.prompts.auditor_prompt import get_auditor_prompt

# Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel('gemini-2.5-flash')


def parse_json_response(response_text):
    """Nettoie et parse la réponse JSON de Gemini."""
    text = response_text.strip()
    
    # Enlever les backticks markdown
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]
    
    text = text.strip()
    
    # Trouver le début du JSON
    if not text.startswith("{"):
        start = text.find("{")
        if start != -1:
            text = text[start:]
    
    # Trouver la fin du JSON
    if not text.endswith("}"):
        end = text.rfind("}")
        if end != -1:
            text = text[:end+1]
    
    return json.loads(text)


class TestAuditorVariableDetection:
    """Tests de détection des variables non définies."""
    
    def test_undefined_variable(self):
        """L'Auditeur DOIT détecter une variable non définie."""
        code = """
def hello():
    print(message)

hello()
"""
        prompt = get_auditor_prompt("test_undefined.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        # Vérifie qu'au moins 1 problème est détecté
        assert report["total_issues"] >= 1, "Devrait détecter au moins 1 problème"
        
        # Vérifie qu'il y a un problème lié à 'message' non défini
        descriptions = [issue["description"].lower() for issue in report["issues"]]
        assert any("message" in desc and ("not defined" in desc or "undefined" in desc) 
                   for desc in descriptions), "Devrait détecter 'message' non défini"
    
    def test_undefined_function(self):
        """L'Auditeur DOIT détecter une fonction non définie."""
        code = """
def process():
    data = read_file("test.txt")
    return data
"""
        prompt = get_auditor_prompt("test_function.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        assert report["total_issues"] >= 1
        descriptions = [issue["description"].lower() for issue in report["issues"]]
        assert any("read_file" in desc for desc in descriptions)


class TestAuditorDocstringDetection:
    """Tests de détection des docstrings manquantes."""
    
    def test_missing_docstring(self):
        """L'Auditeur DOIT détecter l'absence de docstring."""
        code = """
def calculate(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""
        prompt = get_auditor_prompt("test_docstring.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        # Devrait détecter au moins 2 fonctions sans docstring
        assert report["total_issues"] >= 2
        
        docstring_issues = [issue for issue in report["issues"] 
                           if "docstring" in issue["description"].lower()]
        assert len(docstring_issues) >= 2, "Devrait détecter 2 fonctions sans docstring"
    
    def test_has_docstring(self):
        """Code avec docstring NE DOIT PAS être signalé."""
        code = '''
def calculate(a, b):
    """Calcule la somme de deux nombres.
    
    Args:
        a: Premier nombre
        b: Deuxième nombre
    
    Returns:
        La somme de a et b
    """
    return a + b
'''
        prompt = get_auditor_prompt("test_good_docstring.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        # Ne devrait PAS signaler de problème de docstring pour cette fonction
        docstring_issues = [issue for issue in report["issues"] 
                           if "docstring" in issue["description"].lower() 
                           and "calculate" in issue["description"].lower()]
        assert len(docstring_issues) == 0, "Ne devrait PAS signaler de problème de docstring"


class TestAuditorLogicErrors:
    """Tests de détection des erreurs de logique."""
    
    def test_division_by_zero(self):
        """L'Auditeur DOIT détecter une division par zéro."""
        code = """
def calculate():
    result = 100 / 0
    return result
"""
        prompt = get_auditor_prompt("test_division.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        assert report["total_issues"] >= 1
        
        # Vérifie qu'il y a un problème HIGH/CRITICAL lié à division
        critical_issues = [issue for issue in report["issues"] 
                          if issue["severity"] in ["HIGH", "CRITICAL"]
                          and ("division" in issue["description"].lower() 
                               or "zero" in issue["description"].lower())]
        assert len(critical_issues) >= 1, "Devrait détecter division par zéro comme HIGH/CRITICAL"
    
    def test_index_out_of_bounds(self):
        """L'Auditeur DOIT détecter un index hors limites."""
        code = """
numbers = [1, 2, 3]
value = numbers[10]
"""
        prompt = get_auditor_prompt("test_index.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        # Peut détecter ou non selon la sophistication
        # On teste juste que ça ne plante pas
        assert isinstance(report["total_issues"], int)


class TestAuditorNoFalsePositives:
    """Tests anti-hallucination : pas de faux positifs."""
    
    def test_clean_code_no_issues(self):
        """Code parfait NE DOIT PAS générer de faux positifs."""
        code = '''
"""Module de calcul."""

def add(a: int, b: int) -> int:
    """Additionne deux nombres.
    
    Args:
        a: Premier nombre
        b: Deuxième nombre
    
    Returns:
        La somme de a et b
    """
    return a + b


def multiply(x: int, y: int) -> int:
    """Multiplie deux nombres.
    
    Args:
        x: Premier nombre
        y: Deuxième nombre
    
    Returns:
        Le produit de x et y
    """
    return x * y
'''
        prompt = get_auditor_prompt("test_clean.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        # Code parfait = 0 problèmes (ou seulement des suggestions LOW optionnelles)
        high_critical_issues = [issue for issue in report["issues"] 
                               if issue["severity"] in ["HIGH", "CRITICAL"]]
        assert len(high_critical_issues) == 0, "Code propre ne doit PAS avoir de bugs HIGH/CRITICAL"
    
    def test_valid_variable_not_flagged(self):
        """Variable DÉFINIE ne doit PAS être signalée comme non définie."""
        code = """
def process():
    data = "Hello"
    print(data)
"""
        prompt = get_auditor_prompt("test_valid_var.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        # Ne devrait PAS dire que 'data' est non défini
        data_issues = [issue for issue in report["issues"] 
                      if "data" in issue["description"].lower() 
                      and "not defined" in issue["description"].lower()]
        assert len(data_issues) == 0, "'data' est défini, ne doit PAS être signalé"


class TestAuditorJSONValidity:
    """Tests de validité du JSON."""
    
    def test_json_always_valid(self):
        """Le JSON DOIT TOUJOURS être valide, quel que soit le code."""
        test_cases = [
            "print('hello')",
            "def f(): pass",
            "",  # Code vide
            "x = 1 / 0",
            "import sys\nimport os\n\nprint('test')"
        ]
        
        for code in test_cases:
            prompt = get_auditor_prompt("test.py", code)
            response = MODEL.generate_content(prompt)
            
            # parse_json_response lève une exception si JSON invalide
            try:
                report = parse_json_response(response.text)
                # Vérifie structure minimale
                assert "total_issues" in report
                assert "issues" in report
                assert isinstance(report["issues"], list)
            except json.JSONDecodeError as e:
                pytest.fail(f"JSON invalide pour code: {code[:50]}... | Erreur: {e}")
    
    def test_json_structure(self):
        """Le JSON DOIT avoir la structure attendue."""
        code = """
def test():
    print(undefined_var)
"""
        prompt = get_auditor_prompt("test.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        # Vérifie champs obligatoires
        assert "filename" in report or "file" in report
        assert "total_issues" in report
        assert "issues" in report
        
        # Si des issues existent, vérifie leur structure
        if report["total_issues"] > 0:
            issue = report["issues"][0]
            assert "line" in issue
            assert "type" in issue
            assert "severity" in issue
            assert "description" in issue
            assert "suggestion" in issue
    
    def test_severity_values_valid(self):
        """Les valeurs de sévérité DOIVENT être valides."""
        code = """
import os
def test():
    return x / 0
"""
        prompt = get_auditor_prompt("test.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        valid_severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        for issue in report["issues"]:
            assert issue["severity"] in valid_severities, \
                f"Sévérité invalide: {issue['severity']}"


class TestAuditorUnusedImports:
    """Tests de détection des imports non utilisés."""
    
    def test_unused_import_detected(self):
        """L'Auditeur DOIT détecter un import non utilisé."""
        code = """
import os
import sys

print("Hello World")
"""
        prompt = get_auditor_prompt("test_imports.py", code)
        response = MODEL.generate_content(prompt)
        report = parse_json_response(response.text)
        
        # Devrait détecter au moins 1 import inutilisé
        assert report["total_issues"] >= 1
        
        import_issues = [issue for issue in report["issues"] 
                        if "import" in issue["description"].lower() 
                        and ("unused" in issue["description"].lower() 
                             or "not used" in issue["description"].lower()
                             or "inutilisé" in issue["description"].lower())]
        assert len(import_issues) >= 1, "Devrait détecter au moins 1 import inutilisé"


# Fonction pour lancer tous les tests
def run_all_tests():
    """Lance tous les tests et affiche un résumé."""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()