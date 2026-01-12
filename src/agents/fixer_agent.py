"""
Agent Correcteur (Fixer) - Correction automatique du code
Responsable : Lead Dev (Orchestrateur)
Date : 2026-01-10
"""

import google.generativeai as genai
from typing import Dict
import os

from src.prompts import get_fixer_prompt
from src.utils.logger import log_experiment, ActionType
from src.tools.file_tools import read_file, write_file


class FixerAgent:
    """
    Agent Correcteur - Corrige les bugs selon le rapport de l'Auditeur.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialise l'Agent Correcteur.
        
        Args:
            model_name (str): Nom du modele Gemini a utiliser
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.agent_name = "Fixer_Agent"
    
    def fix_file(self, file_path: str, audit_report: Dict) -> bool:
        """
        Corrige un fichier selon le rapport d'audit.
        
        Args:
            file_path (str): Chemin complet vers le fichier a corriger
            audit_report (dict): Rapport JSON de l'Auditeur
            
        Returns:
            bool: True si correction reussie, False sinon
        """
        
        file_name = os.path.basename(file_path)
        
        print(f"\n{'='*80}")
        print(f"FIXER - Correction de {file_name}")
        print(f"{'='*80}")
        
        bugs_to_fix = audit_report.get("total_issues", 0)
        print(f"Problemes a corriger : {bugs_to_fix}")
        
        if bugs_to_fix == 0:
            print("Code propre - Aucune correction necessaire")
            return True
        
        try:
            buggy_code = read_file(file_path)
        except Exception as e:
            print(f"ERREUR: Impossible de lire le fichier : {e}")
            return False
        
        prompt = get_fixer_prompt(file_name, buggy_code, audit_report)
        
        try:
            print(f"Envoi a {self.model_name}...")
            response = self.model.generate_content(prompt)
            raw_response = response.text.strip()
            
            print(f"Reponse recue ({len(raw_response)} caracteres)")
            
            fixed_code = self._clean_code_response(raw_response)
            
            try:
                compile(fixed_code, file_name, 'exec')
                print("Code corrige syntaxiquement VALIDE")
                syntax_valid = True
            except SyntaxError as e:
                print(f"ATTENTION : Erreur de syntaxe ligne {e.lineno}")
                syntax_valid = False
            
            print(f"Lignes : {len(buggy_code.splitlines())} -> {len(fixed_code.splitlines())}")
            
            try:
                write_file(file_path, fixed_code)
                print(f"Code corrige sauvegarde : {file_path}")
            except Exception as e:
                print(f"ERREUR: Impossible de sauvegarder le fichier : {e}")
                return False
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.FIX,
                details={
                    "file_fixed": file_name,
                    "input_prompt": prompt,
                    "output_response": raw_response,
                    "bugs_fixed": bugs_to_fix,
                    "original_lines": len(buggy_code.splitlines()),
                    "fixed_lines": len(fixed_code.splitlines()),
                    "syntax_valid": syntax_valid
                },
                status="SUCCESS" if syntax_valid else "PARTIAL_SUCCESS"
            )
            
            return syntax_valid
            
        except Exception as e:
            print(f"ERREUR lors de la correction : {e}")
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.FIX,
                details={
                    "file_fixed": file_name,
                    "input_prompt": prompt if 'prompt' in locals() else "N/A",
                    "output_response": "N/A",
                    "error": str(e)
                },
                status="FAILURE"
            )
            
            return False
    
    def _clean_code_response(self, response: str) -> str:
        """
        Nettoie la reponse pour extraire le code Python pur.
        
        Args:
            response (str): Reponse brute de Gemini
            
        Returns:
            str: Code Python nettoye
        """
        cleaned = response.strip()
        
        if cleaned.startswith("```python"):
            cleaned = cleaned[9:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()