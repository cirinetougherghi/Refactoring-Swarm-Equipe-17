"""
Agent Testeur (Judge) - Validation par tests
Responsable : Lead Dev (Orchestrateur)
Date : 2026-01-10
Version : 1.1 - Fixed to handle no-test scenarios
"""

import json
import google.generativeai as genai
from typing import Dict, Optional
import os

from src.prompts import get_judge_prompt
from src.utils.logger import log_experiment, ActionType
from src.tools.analysis_tools import run_pytest
from src.tools.file_tools import read_file


class JudgeAgent:
    """
    Agent Testeur - Execute pytest et decide de valider ou renvoyer au Correcteur.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialise l'Agent Testeur.
        
        Args:
            model_name (str): Nom du modele Gemini a utiliser
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.agent_name = "Judge_Agent"
    
    def judge_file(self, file_path: str, audit_report: Optional[Dict] = None) -> Optional[Dict]:
        """
        Execute pytest et analyse les resultats.
        Si aucun test unitaire n'existe, valide le code s'il est propre.
        
        Args:
            file_path (str): Chemin complet vers le fichier a tester
            audit_report (dict, optional): Rapport d'audit pour validation sans tests
            
        Returns:
            dict: Rapport du Testeur avec decision (VALIDATE ou PASS_TO_FIXER)
        """
        
        file_name = os.path.basename(file_path)
        
        print(f"\n{'='*80}")
        print(f"JUDGE - Test de {file_name}")
        print(f"{'='*80}")
        
        # NOUVELLE LOGIQUE : Si aucun bug détecté et code valide → VALIDATE
        if audit_report is not None:
            bugs_found = audit_report.get("total_issues", 0)
            
            if bugs_found == 0:
                # Vérifie que le code est syntaxiquement valide
                try:
                    code = read_file(file_path)
                    compile(code, file_name, 'exec')
                    
                    print(f"Code propre (0 bugs) et syntaxe valide")
                    print(f"Decision : VALIDATE (aucun test unitaire requis)")
                    
                    judge_report = {
                        "decision": "VALIDATE",
                        "passed": 0,
                        "failed": 0,
                        "message": "Code propre, syntaxe valide, aucun bug détecté",
                        "validation_method": "audit_only"
                    }
                    
                    log_experiment(
                        agent_name=self.agent_name,
                        model_used=self.model_name,
                        action=ActionType.DEBUG,
                        details={
                            "file_tested": file_name,
                            "input_prompt": "Validation sans tests unitaires",
                            "output_response": json.dumps(judge_report),
                            "decision": "VALIDATE",
                            "tests_passed": 0,
                            "tests_failed": 0,
                            "bugs_in_audit": bugs_found,
                            "validation_method": "audit_only"
                        },
                        status="SUCCESS"
                    )
                    
                    return judge_report
                    
                except SyntaxError as e:
                    print(f"ERREUR: Code invalide malgré 0 bugs détectés : {e}")
                    # Continue avec pytest normal
        
        # LOGIQUE NORMALE : Exécute pytest
        try:
            pytest_result = run_pytest(file_path)
        except Exception as e:
            print(f"ERREUR: Impossible d'executer pytest : {e}")
            return None
        
        passed = pytest_result.get("passed", 0)
        failed = pytest_result.get("failed", 0)
        stdout = pytest_result.get("stdout", "")
        stderr = pytest_result.get("stderr", "")
        returncode = pytest_result.get("returncode", 1)
        
        pytest_output = stdout + "\n" + stderr
        
        if not pytest_output.strip():
            print("ERREUR: Aucune sortie pytest")
            return None
        
        print(f"Sortie pytest ({len(pytest_output)} caracteres)")
        print(f"   Tests passes : {passed}")
        print(f"   Tests echoues : {failed}")
        
        # NOUVELLE LOGIQUE : Si 0 tests trouvés et code propre → VALIDATE
        if passed == 0 and failed == 0:
            if audit_report is not None and audit_report.get("total_issues", 0) == 0:
                print(f"Aucun test unitaire trouve, mais code propre")
                print(f"Decision : VALIDATE")
                
                judge_report = {
                    "decision": "VALIDATE",
                    "passed": 0,
                    "failed": 0,
                    "message": "Aucun test unitaire, mais code propre et valide",
                    "validation_method": "no_tests_clean_code"
                }
                
                log_experiment(
                    agent_name=self.agent_name,
                    model_used=self.model_name,
                    action=ActionType.DEBUG,
                    details={
                        "file_tested": file_name,
                        "input_prompt": "Validation sans tests (code propre)",
                        "output_response": json.dumps(judge_report),
                        "decision": "VALIDATE",
                        "tests_passed": 0,
                        "tests_failed": 0,
                        "pytest_returncode": returncode,
                        "validation_method": "no_tests_clean_code"
                    },
                    status="SUCCESS"
                )
                
                return judge_report
        
        # LOGIQUE ORIGINALE : Demande à Gemini d'analyser la sortie pytest
        prompt = get_judge_prompt(file_name, pytest_output)
        
        try:
            print(f"Envoi a {self.model_name}...")
            response = self.model.generate_content(prompt)
            raw_response = response.text.strip()
            
            print(f"Reponse recue ({len(raw_response)} caracteres)")
            
            cleaned_response = self._clean_json_response(raw_response)
            
            judge_report = json.loads(cleaned_response)
            
            decision = judge_report.get("decision", "UNKNOWN")
            judge_passed = judge_report.get("passed", 0)
            judge_failed = judge_report.get("failed", 0)
            
            print(f"Tests : {judge_passed} passes, {judge_failed} echoues")
            print(f"Decision : {decision}")
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "file_tested": file_name,
                    "input_prompt": prompt,
                    "output_response": raw_response,
                    "decision": decision,
                    "tests_passed": judge_passed,
                    "tests_failed": judge_failed,
                    "pytest_returncode": returncode,
                    "pytest_output": pytest_output[:500]
                },
                status="SUCCESS"
            )
            
            return judge_report
            
        except json.JSONDecodeError as e:
            print(f"ERREUR : JSON invalide du Testeur")
            print(f"   {e}")
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "file_tested": file_name,
                    "input_prompt": prompt if 'prompt' in locals() else "N/A",
                    "output_response": raw_response if 'raw_response' in locals() else "N/A",
                    "error": str(e)
                },
                status="FAILURE"
            )
            
            return None
            
        except Exception as e:
            print(f"ERREUR lors du jugement : {e}")
            
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "file_tested": file_name,
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