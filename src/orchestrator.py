"""
Orchestrateur - Gestion du workflow multi-agents
Responsable : Lead Dev (Orchestrateur)
Date : 2026-01-10
Version : 1.1 - Pass audit_report to judge for better validation
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import google.generativeai as genai

from src.agents import AuditorAgent, FixerAgent, JudgeAgent
from src.tools.file_tools import read_file, write_file
from src.utils.logger import log_experiment, ActionType


@dataclass
class WorkflowState:
    """Etat du workflow pour un fichier."""
    file_name: str
    file_path: str
    current_code: str
    original_code: str
    iteration: int
    audit_report: Optional[Dict] = None
    judge_report: Optional[Dict] = None
    status: str = "PENDING"
    total_bugs_found: int = 0
    total_bugs_fixed: int = 0


class Orchestrator:
    """
    Orchestrateur - Gere le workflow complet de refactoring.
    """
    
    def __init__(self, target_dir: str, max_iterations: int = 10):
        """
        Initialise l'Orchestrateur.
        
        Args:
            target_dir (str): Dossier contenant les fichiers Python a traiter
            max_iterations (int): Nombre maximum d'iterations par fichier (defaut: 10)
        """
        self.target_dir = target_dir
        self.max_iterations = max_iterations
        
        self.auditor = AuditorAgent()
        self.fixer = FixerAgent()
        self.judge = JudgeAgent()
        
        self.files_processed: List[WorkflowState] = []
        self.total_files = 0
        self.files_validated = 0
        self.files_failed = 0
        
        print(f"\n{'='*80}")
        print(f"ORCHESTRATOR INITIALISE")
        print(f"{'='*80}")
        print(f"Dossier cible : {target_dir}")
        print(f"Max iterations : {max_iterations}")
        print(f"{'='*80}\n")
    
    def run(self) -> Dict:
        """
        Execute le workflow complet sur tous les fichiers Python du dossier cible.
        
        Returns:
            dict: Resume des resultats
        """
        
        if not os.path.exists(self.target_dir):
            print(f"ERREUR : Dossier '{self.target_dir}' introuvable")
            return self._generate_summary()
        
        python_files = self._find_python_files()
        
        if not python_files:
            print(f"ATTENTION : Aucun fichier Python trouve dans '{self.target_dir}'")
            return self._generate_summary()
        
        self.total_files = len(python_files)
        print(f"Fichiers Python trouves : {self.total_files}")
        print(f"{'='*80}\n")
        
        for file_path in python_files:
            self._process_file(file_path)
        
        summary = self._generate_summary()
        self._print_final_summary(summary)
        
        return summary
    
    def _find_python_files(self) -> List[str]:
        """
        Trouve tous les fichiers Python dans le dossier cible.
        
        Returns:
            list: Liste des chemins complets vers les fichiers .py
        """
        python_files = []
        
        for root, dirs, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
        
        return python_files
    
    def _process_file(self, file_path: str) -> None:
        """
        Traite un fichier Python avec le workflow complet.
        
        Args:
            file_path (str): Chemin complet vers le fichier
        """
        file_name = os.path.basename(file_path)
        
        print(f"\n{'#'*80}")
        print(f"TRAITEMENT : {file_name}")
        print(f"{'#'*80}\n")
        
        try:
            original_code = read_file(file_path)
        except Exception as e:
            print(f"ERREUR: Impossible de lire le fichier : {e}")
            return
        
        state = WorkflowState(
            file_name=file_name,
            file_path=file_path,
            current_code=original_code,
            original_code=original_code,
            iteration=0
        )
        
        while state.iteration < self.max_iterations:
            state.iteration += 1
            
            print(f"\n{'='*80}")
            print(f"ITERATION {state.iteration}/{self.max_iterations}")
            print(f"{'='*80}")
            
            # ETAPE 1 : AUDIT
            audit_report = self.auditor.analyze_file(file_path)
            
            if audit_report is None:
                print(f"ERREUR: Audit echoue - Arret du traitement")
                state.status = "FAILED"
                break
            
            state.audit_report = audit_report
            bugs_found = audit_report.get("total_issues", 0)
            state.total_bugs_found += bugs_found
            
            if bugs_found == 0:
                print(f"Code propre - Aucun bug detecte")
                
                # ✅ CHANGEMENT ICI : Passer audit_report au judge
                judge_report = self.judge.judge_file(file_path, audit_report)
                
                if judge_report and judge_report.get("decision") == "VALIDATE":
                    state.status = "VALIDATED"
                    state.judge_report = judge_report
                    self.files_validated += 1
                    print(f"\n✅ {file_name} VALIDE !")
                    break
                else:
                    print(f"ATTENTION: Tests ont echoue malgre l'absence de bugs detectes")
                    state.status = "FAILED"
                    break
            
            # ETAPE 2 : FIX
            fix_success = self.fixer.fix_file(file_path, audit_report)
            
            if not fix_success:
                print(f"ERREUR: Correction echouee - Arret du traitement")
                state.status = "FAILED"
                break
            
            state.current_code = read_file(file_path)
            state.total_bugs_fixed += bugs_found
            
            # ETAPE 3 : TEST
            # ✅ CHANGEMENT ICI : Passer audit_report au judge
            judge_report = self.judge.judge_file(file_path, audit_report)
            
            if judge_report is None:
                print(f"ERREUR: Test echoue - Arret du traitement")
                state.status = "FAILED"
                break
            
            state.judge_report = judge_report
            decision = judge_report.get("decision")
            
            if decision == "VALIDATE":
                state.status = "VALIDATED"
                self.files_validated += 1
                print(f"\n✅ {file_name} VALIDE !")
                break
            
            elif decision == "PASS_TO_FIXER":
                print(f"\nATTENTION: Tests echoues - Nouvelle iteration necessaire")
                
                if state.iteration >= self.max_iterations:
                    state.status = "MAX_ITERATIONS"
                    self.files_failed += 1
                    print(f"\nATTENTION: Limite de {self.max_iterations} iterations atteinte")
                    break
                
                continue
            
            else:
                print(f"ERREUR: Decision inconnue du Judge : {decision}")
                state.status = "FAILED"
                break
        
        self.files_processed.append(state)
        
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "file": file_name,
                "input_prompt": f"Process file: {file_name}",
                "output_response": f"Status: {state.status}",
                "iterations": state.iteration,
                "bugs_found": state.total_bugs_found,
                "bugs_fixed": state.total_bugs_fixed,
                "final_status": state.status
            },
            status="SUCCESS" if state.status == "VALIDATED" else "PARTIAL_SUCCESS"
        )
    
    def _generate_summary(self) -> Dict:
        """
        Genere le resume des resultats.
        
        Returns:
            dict: Resume complet
        """
        summary = {
            "total_files": self.total_files,
            "files_validated": self.files_validated,
            "files_failed": self.files_failed,
            "success_rate": (self.files_validated / self.total_files * 100) if self.total_files > 0 else 0,
            "files": []
        }
        
        for state in self.files_processed:
            summary["files"].append({
                "file_name": state.file_name,
                "status": state.status,
                "iterations": state.iteration,
                "bugs_found": state.total_bugs_found,
                "bugs_fixed": state.total_bugs_fixed
            })
        
        return summary
    
    def _print_final_summary(self, summary: Dict) -> None:
        """
        Affiche le resume final dans la console.
        
        Args:
            summary (dict): Resume a afficher
        """
        print(f"\n{'#'*80}")
        print(f"RESUME FINAL")
        print(f"{'#'*80}\n")
        
        print(f"Fichiers traites : {summary['total_files']}")
        print(f"Valides : {summary['files_validated']}")
        print(f"Echoues : {summary['files_failed']}")
        print(f"Taux de succes : {summary['success_rate']:.1f}%\n")
        
        if summary['files']:
            print(f"{'─'*80}")
            print(f"DETAILS PAR FICHIER")
            print(f"{'─'*80}\n")
            
            for file_info in summary['files']:
                status_symbol = "[OK]" if file_info['status'] == "VALIDATED" else "[FAIL]"
                print(f"{status_symbol} {file_info['file_name']}")
                print(f"   Status: {file_info['status']}")
                print(f"   Iterations: {file_info['iterations']}")
                print(f"   Bugs trouves: {file_info['bugs_found']}")
                print(f"   Bugs corriges: {file_info['bugs_fixed']}\n")
        
        print(f"{'#'*80}\n")