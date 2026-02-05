"""
Agent Auditeur - Analyse du code Python
Responsable : Lead Dev (Orchestrateur)
Date : 2026-01-10
"""

import json
import google.generativeai as genai
from typing import Dict, Optional
import os

from src.prompts import get_auditor_prompt
from src.utils.logger import log_experiment, ActionType
from src.tools.file_tools import read_file


class AuditorAgent:
    """
    Agent Auditeur - Detecte les bugs et problemes de qualite dans le code Python.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialise l'Agent Auditeur.
        
        Args:
            model_name (str): Nom du modele Gemini a utiliser
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.agent_name = "Auditor_Agent"
    
    def analyze_file(self, file_path: str) -> Optional[Dict]:
        """
        Analyse un fichier Python et produit un rapport JSON.
        
        Args:
            file_path (str): Chemin complet vers le fichier a analyser
            
        Returns:
            dict: Rapport d'audit au format JSON, ou None si erreur
        """
        
        try:
            code_content = read_file(file_path)
        except Exception as e:
            print(f"ERREUR: Impossible de lire le fichier : {e}")
            return None
        
        file_name = os.path.basename(file_path)
        
        print(f"\n{'='*80}")
        print(f"AUDITOR - Analyse de {file_name}")
        print(f"{'='*80}")
        
        prompt = get_auditor_prompt(file_name, code_content)
        
        try:
            print(f"Envoi a {self.model_name}...")
            response = self.model.generate_content(prompt)
            raw_response = response.text.strip()
            
            print(f"Reponse recue ({len(raw_response)} caracteres)")
            
            cleaned_response = self._clean_json_response(raw_response)
            
            audit_report = json.loads(cleaned_response)
            
            bugs_found = audit_report.get("total_issues", 0)
            print(f"Resultat : {bugs_found} probleme(s) detecte(s)")
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": file_name,
                    "input_prompt": prompt,
                    "output_response": raw_response,
                    "bugs_found": bugs_found,
                    "code_lines": len(code_content.splitlines())
                },
                status="SUCCESS"
            )
            
            return audit_report
            
        except json.JSONDecodeError as e:
            print(f"ERREUR : JSON invalide de l'Auditeur")
            print(f"   {e}")
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": file_name,
                    "input_prompt": prompt,
                    "output_response": raw_response if 'raw_response' in locals() else "N/A",
                    "error": str(e)
                },
                status="FAILURE"
            )
            
            return None
            
        except Exception as e:
            print(f"ERREUR lors de l'analyse : {e}")
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": file_name,
                    "input_prompt": prompt if 'prompt' in locals() else "N/A",
                    "output_response": "N/A",
                    "error": str(e)
                },
                status="FAILURE"
            )
            
            return None
    
    def _clean_json_response(self, response: str) -> str:
        """
        Nettoie la reponse pour extraire le JSON pur.
        
        Args:
            response (str): Reponse brute de Gemini
            
        Returns:
            str: JSON nettoye
        """
        cleaned = response.strip()
        
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()