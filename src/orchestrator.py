"""
Orchestrateur - Gestion du workflow multi-agents
Responsable : Lead Dev (Orchestrateur) + Data Officer (Logging)
Date : 2026-01-30
Version : 2.0 - Complete logging integration + Rate limiting
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import google.generativeai as genai

from src.agents import AuditorAgent, FixerAgent, JudgeAgent
from src.tools.file_tools import read_file, write_file
from src.utils.logger import log_experiment, ActionType
from src.utils.rate_limiter import wait_for_rate_limit  # ✅ NEW: Rate limiting


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
    
    **LOGGING COMPLET POUR TP IGL 2025-2026:**
    - Initialisation (GENERATION)
    - Scan de répertoire (ANALYSIS)
    - Traitement de chaque fichier (ANALYSIS)
    - Chaque itération (ANALYSIS)
    - Résumé final (GENERATION)
    
    **RATE LIMITING:**
    - Les agents appellent Gemini API
    - Rate limiting géré au niveau des agents
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
        
        # ✅ NEW: LOG - Orchestrator initialization
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.GENERATION,
            details={
                "operation": "orchestrator_initialization",
                "input_prompt": f"Initializing orchestrator for directory: {target_dir}",
                "output_response": f"Orchestrator initialized. Target: {target_dir}, Max iterations: {max_iterations}",
                "target_directory": target_dir,
                "max_iterations": max_iterations,
                "agents_initialized": ["AuditorAgent", "FixerAgent", "JudgeAgent"]
            },
            status="SUCCESS"
        )

    def run(self) -> Dict:
        """
        Execute le workflow complet sur tous les fichiers Python du dossier cible.

        Returns:
            dict: Resume des resultats
        """

        if not os.path.exists(self.target_dir):
            print(f"ERREUR : Dossier '{self.target_dir}' introuvable")
            
            # ✅ NEW: LOG - Directory not found
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.ANALYSIS,
                details={
                    "operation": "directory_scan_failed",
                    "input_prompt": f"Attempting to scan directory: {self.target_dir}",
                    "output_response": f"ERROR: Directory not found: {self.target_dir}",
                    "target_directory": self.target_dir,
                    "error": "Directory does not exist"
                },
                status="FAILURE"
            )
            
            return self._generate_summary()

        python_files = self._find_python_files()

        if not python_files:
            print(f"ATTENTION : Aucun fichier Python trouve dans '{self.target_dir}'")
            
            # ✅ NEW: LOG - No Python files found
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.ANALYSIS,
                details={
                    "operation": "no_files_found",
                    "input_prompt": f"Scanning for Python files in: {self.target_dir}",
                    "output_response": "No Python files found in target directory",
                    "target_directory": self.target_dir,
                    "files_found": 0
                },
                status="FAILURE"
            )
            
            return self._generate_summary()

        self.total_files = len(python_files)
        print(f"Fichiers Python trouves : {self.total_files}")
        print(f"{'='*80}\n")
        
        # ✅ NEW: LOG - Files discovered
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "operation": "files_discovered",
                "input_prompt": f"Completed directory scan: {self.target_dir}",
                "output_response": f"Found {self.total_files} Python files ready for processing",
                "target_directory": self.target_dir,
                "files_found": python_files,
                "file_count": self.total_files
            },
            status="SUCCESS"
        )

        for file_path in python_files:
            self._process_file(file_path)

        summary = self._generate_summary()
        self._print_final_summary(summary)
        
        # ✅ NEW: LOG - Workflow completion
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.GENERATION,
            details={
                "operation": "workflow_complete",
                "input_prompt": f"Completed refactoring workflow for {self.total_files} files",
                "output_response": f"Workflow finished. Validated: {self.files_validated}, Failed: {self.files_failed}, Success rate: {summary['success_rate']:.1f}%",
                "total_files": self.total_files,
                "files_validated": self.files_validated,
                "files_failed": self.files_failed,
                "success_rate": summary['success_rate'],
                "summary": summary
            },
            status="SUCCESS"
        )

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
        
        # ✅ NEW: LOG - File processing start
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "operation": "file_processing_start",
                "input_prompt": f"Starting workflow for file: {file_name}",
                "output_response": f"Initializing {self.max_iterations}-iteration workflow for {file_name}",
                "file_path": file_path,
                "file_name": file_name,
                "max_iterations": self.max_iterations
            },
            status="SUCCESS"
        )

        try:
            original_code = read_file(file_path)
        except Exception as e:
            print(f"ERREUR: Impossible de lire le fichier : {e}")
            
            # ✅ NEW: LOG - File read error
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.ANALYSIS,
                details={
                    "operation": "file_read_failed",
                    "input_prompt": f"Attempting to read file: {file_path}",
                    "output_response": f"ERROR: Cannot read file: {str(e)}",
                    "file_path": file_path,
                    "error": str(e)
                },
                status="FAILURE"
            )
            
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
            
            # ✅ NEW: LOG - Iteration start
            log_experiment(
                agent_name="Orchestrator",
                model_used="N/A",
                action=ActionType.ANALYSIS,
                details={
                    "operation": "iteration_start",
                    "input_prompt": f"Starting iteration {state.iteration}/{self.max_iterations} for {file_name}",
                    "output_response": f"Beginning iteration {state.iteration}: Audit → Fix → Judge",
                    "file_name": file_name,
                    "iteration": state.iteration,
                    "max_iterations": self.max_iterations
                },
                status="SUCCESS"
            )

            # ETAPE 1 : AUDIT
            # ✅ RATE LIMITING: Auditor calls Gemini API internally
            wait_for_rate_limit()  # Wait before agent makes API call
            audit_report = self.auditor.analyze_file(file_path)

            if audit_report is None:
                print(f"ERREUR: Audit echoue - Arret du traitement")
                state.status = "FAILED"
                
                # ✅ NEW: LOG - Audit failure
                log_experiment(
                    agent_name="Orchestrator",
                    model_used="N/A",
                    action=ActionType.ANALYSIS,
                    details={
                        "operation": "audit_failed_workflow_stopped",
                        "input_prompt": f"Audit failed for {file_name} at iteration {state.iteration}",
                        "output_response": "Stopping workflow due to audit failure",
                        "file_name": file_name,
                        "iteration": state.iteration,
                        "reason": "audit_error"
                    },
                    status="FAILURE"
                )
                
                break

            state.audit_report = audit_report
            bugs_found = audit_report.get("total_issues", 0)
            state.total_bugs_found += bugs_found

            if bugs_found == 0:
                print(f"Code propre - Aucun bug detecte")

                # ✅ RATE LIMITING: Judge calls Gemini API internally
                wait_for_rate_limit()  # Wait before agent makes API call
                judge_report = self.judge.judge_file(file_path, audit_report)

                if judge_report and judge_report.get("decision") == "VALIDATE":
                    state.status = "VALIDATED"
                    state.judge_report = judge_report
                    self.files_validated += 1
                    print(f"\n✅ {file_name} VALIDE !")
                    
                    # ✅ NEW: LOG - Early validation (clean code)
                    log_experiment(
                        agent_name="Orchestrator",
                        model_used="N/A",
                        action=ActionType.ANALYSIS,
                        details={
                            "operation": "early_validation",
                            "input_prompt": f"File {file_name} validated at iteration {state.iteration}",
                            "output_response": f"File validated early - no bugs found, tests passed",
                            "file_name": file_name,
                            "iteration": state.iteration,
                            "bugs_found": 0,
                            "reason": "clean_code"
                        },
                        status="SUCCESS"
                    )
                    
                    break
                else:
                    print(f"ATTENTION: Tests ont echoue malgre l'absence de bugs detectes")
                    state.status = "FAILED"
                    
                    # ✅ NEW: LOG - Tests failed despite clean audit
                    log_experiment(
                        agent_name="Orchestrator",
                        model_used="N/A",
                        action=ActionType.DEBUG,
                        details={
                            "operation": "tests_failed_clean_code",
                            "input_prompt": f"Tests failed for {file_name} despite clean audit",
                            "output_response": "Stopping workflow - tests failed with clean code",
                            "file_name": file_name,
                            "iteration": state.iteration,
                            "bugs_found": 0,
                            "reason": "test_failure"
                        },
                        status="FAILURE"
                    )
                    
                    break

            # ETAPE 2 : FIX
            # ✅ RATE LIMITING: Fixer calls Gemini API internally
            wait_for_rate_limit()  # Wait before agent makes API call
            fix_success = self.fixer.fix_file(file_path, audit_report)

            if not fix_success:
                print(f"ERREUR: Correction echouee - Arret du traitement")
                state.status = "FAILED"
                
                # ✅ NEW: LOG - Fix failure
                log_experiment(
                    agent_name="Orchestrator",
                    model_used="N/A",
                    action=ActionType.FIX,
                    details={
                        "operation": "fix_failed_workflow_stopped",
                        "input_prompt": f"Fix failed for {file_name} at iteration {state.iteration}",
                        "output_response": "Stopping workflow due to fix failure",
                        "file_name": file_name,
                        "iteration": state.iteration,
                        "bugs_to_fix": bugs_found,
                        "reason": "fix_error"
                    },
                    status="FAILURE"
                )
                
                break

            state.current_code = read_file(file_path)
            state.total_bugs_fixed += bugs_found

            # ETAPE 3 : TEST
            # ✅ RATE LIMITING: Judge calls Gemini API internally
            wait_for_rate_limit()  # Wait before agent makes API call
            judge_report = self.judge.judge_file(file_path, audit_report)

            if judge_report is None:
                print(f"ERREUR: Test echoue - Arret du traitement")
                state.status = "FAILED"
                
                # ✅ NEW: LOG - Judge failure
                log_experiment(
                    agent_name="Orchestrator",
                    model_used="N/A",
                    action=ActionType.DEBUG,
                    details={
                        "operation": "judge_failed_workflow_stopped",
                        "input_prompt": f"Judge failed for {file_name} at iteration {state.iteration}",
                        "output_response": "Stopping workflow due to judge failure",
                        "file_name": file_name,
                        "iteration": state.iteration,
                        "reason": "judge_error"
                    },
                    status="FAILURE"
                )
                
                break

            state.judge_report = judge_report
            decision = judge_report.get("decision")

            if decision == "VALIDATE":
                state.status = "VALIDATED"
                self.files_validated += 1
                print(f"\n✅ {file_name} VALIDE !")
                
                # ✅ NEW: LOG - File validated
                log_experiment(
                    agent_name="Orchestrator",
                    model_used="N/A",
                    action=ActionType.ANALYSIS,
                    details={
                        "operation": "file_validated",
                        "input_prompt": f"File {file_name} validated at iteration {state.iteration}",
                        "output_response": f"File successfully validated after {state.iteration} iterations",
                        "file_name": file_name,
                        "iteration": state.iteration,
                        "bugs_fixed": state.total_bugs_fixed,
                        "reason": "judge_approved"
                    },
                    status="SUCCESS"
                )
                
                break

            elif decision == "PASS_TO_FIXER":
                print(f"\nATTENTION: Tests echoues - Nouvelle iteration necessaire")

                if state.iteration >= self.max_iterations:
                    state.status = "MAX_ITERATIONS"
                    self.files_failed += 1
                    print(f"\nATTENTION: Limite de {self.max_iterations} iterations atteinte")
                    
                    # ✅ NEW: LOG - Max iterations reached
                    log_experiment(
                        agent_name="Orchestrator",
                        model_used="N/A",
                        action=ActionType.DEBUG,
                        details={
                            "operation": "max_iterations_reached",
                            "input_prompt": f"File {file_name} reached max iterations",
                            "output_response": f"Stopping workflow - max {self.max_iterations} iterations reached",
                            "file_name": file_name,
                            "iteration": state.iteration,
                            "max_iterations": self.max_iterations,
                            "reason": "max_iterations"
                        },
                        status="FAILURE"
                    )
                    
                    break

                # ✅ NEW: LOG - Continue to next iteration
                log_experiment(
                    agent_name="Orchestrator",
                    model_used="N/A",
                    action=ActionType.ANALYSIS,
                    details={
                        "operation": "iteration_continue",
                        "input_prompt": f"Tests failed for {file_name}, continuing to iteration {state.iteration + 1}",
                        "output_response": "Judge requested another iteration - continuing workflow",
                        "file_name": file_name,
                        "current_iteration": state.iteration,
                        "next_iteration": state.iteration + 1,
                        "reason": "tests_failed"
                    },
                    status="SUCCESS"
                )
                
                continue

            else:
                print(f"ERREUR: Decision inconnue du Judge : {decision}")
                state.status = "FAILED"
                
                # ✅ NEW: LOG - Unknown judge decision
                log_experiment(
                    agent_name="Orchestrator",
                    model_used="N/A",
                    action=ActionType.DEBUG,
                    details={
                        "operation": "unknown_judge_decision",
                        "input_prompt": f"Unknown judge decision for {file_name}: {decision}",
                        "output_response": "Stopping workflow - unknown decision",
                        "file_name": file_name,
                        "iteration": state.iteration,
                        "decision": decision,
                        "reason": "invalid_decision"
                    },
                    status="FAILURE"
                )
                
                break

        self.files_processed.append(state)

        # ✅ EXISTING LOG (kept and enhanced)
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.ANALYSIS,
            details={
                "operation": "file_processing_complete",
                "file": file_name,
                "input_prompt": f"Completed processing file: {file_name}",
                "output_response": f"File processing finished. Status: {state.status}, Iterations: {state.iteration}, Bugs found: {state.total_bugs_found}, Bugs fixed: {state.total_bugs_fixed}",
                "file_path": file_path,
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