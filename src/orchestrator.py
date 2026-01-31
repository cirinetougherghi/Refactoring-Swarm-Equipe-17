"""
Orchestrateur - Gestion du workflow multi-agents
Responsable : Lead Dev (Orchestrateur)
Date : 2026-01-31
Version : 2.0 - LangGraph Integration (Logique v1.1 préservée à 100%)


"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import google.generativeai as genai

from src.agents import AuditorAgent, FixerAgent, JudgeAgent
from src.workflow_graph import refactoring_graph  # ← MODIFICATION 1 : Import du graphe
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
        
        # MODIFICATION 2 : Les agents sont maintenant créés dans les nœuds du graphe
        # self.auditor = AuditorAgent()
        # self.fixer = FixerAgent()
        # self.judge = JudgeAgent()
        
        self.files_processed: List[WorkflowState] = []
        self.total_files = 0
        self.files_validated = 0
        self.files_failed = 0
        
        print(f"\n{'='*80}")
        print(f"ORCHESTRATOR INITIALISE (LangGraph v2.0)")  # ← MODIFICATION 3
        print(f"{'='*80}")
        print(f"Dossier cible : {target_dir}")
        print(f"Max iterations : {max_iterations}")
        print(f"{'='*80}\n")
    
    def run(self) -> Dict:
        """
        Execute le workflow complet sur tous les fichiers Python du dossier cible.
        
        IDENTIQUE À v1.1 - AUCUNE MODIFICATION
        
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
        
        IDENTIQUE À v1.1 - AUCUNE MODIFICATION
        
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
        Traite un fichier Python avec le graphe LangGraph.
        
        MODIFICATION 4 : Remplace la boucle while par refactoring_graph.invoke()
        La logique métier reste IDENTIQUE (elle est dans workflow_graph.py)
        
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
            self.files_failed += 1  # Incrémenter le compteur d'échecs
            return
        
        # Préparer l'état initial pour LangGraph
        # Structure identique à WorkflowState de v1.1
        initial_state = {
            "file_path": file_path,
            "file_name": file_name,
            "iteration": 0,
            "max_iterations": self.max_iterations,
            "audit_report": {},
            "judge_report": {},
            "status": "PENDING",
            "total_bugs_found": 0,
            "total_bugs_fixed": 0,
            "original_code": original_code,
            "current_code": original_code
        }
        
        # ═══════════════════════════════════════════════════════════
        # EXÉCUTION DU GRAPHE LANGGRAPH
        # Remplace la boucle while des lignes 164-232 de v1.1
        # La logique exacte est préservée dans workflow_graph.py
        # ═══════════════════════════════════════════════════════════
        
        try:
            final_state = refactoring_graph.invoke(initial_state)
            
        except Exception as e:
            print(f"\n❌ ERREUR lors de l'exécution du graphe : {e}")
            import traceback
            traceback.print_exc()
            
            final_state = {
                **initial_state,
                "status": "FAILED",
                "iteration": 0
            }
        
        # ═══════════════════════════════════════════════════════════
        # TRAITEMENT DES RÉSULTATS
        # IDENTIQUE À v1.1 - Créer WorkflowState et mettre à jour compteurs
        # ═══════════════════════════════════════════════════════════
        
        # Créer l'objet WorkflowState pour compatibilité avec v1.1
        state = WorkflowState(
            file_name=file_name,
            file_path=file_path,
            current_code=final_state.get("current_code", original_code),
            original_code=original_code,
            iteration=final_state.get("iteration", 0),
            audit_report=final_state.get("audit_report", {}),
            judge_report=final_state.get("judge_report", {}),
            status=final_state.get("status", "FAILED"),
            total_bugs_found=final_state.get("total_bugs_found", 0),
            total_bugs_fixed=final_state.get("total_bugs_fixed", 0)
        )
        
        self.files_processed.append(state)
        
        # Mise à jour des compteurs (IDENTIQUE à v1.1)
        if state.status == "VALIDATED":
            self.files_validated += 1
        else:
            self.files_failed += 1
        
        # Logging pour l'analyse scientifique
        # IDENTIQUE à v1.1 avec ajout du champ "workflow_engine"
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
                "final_status": state.status,
                "workflow_engine": "LangGraph_v2.0"  # ← Seule nouveauté dans les logs
            },
            status="SUCCESS" if state.status == "VALIDATED" else "PARTIAL_SUCCESS"
        )
    
    def _generate_summary(self) -> Dict:
        """
        Genere le resume des resultats.
        
        IDENTIQUE À v1.1 - AUCUNE MODIFICATION
        
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
        
        IDENTIQUE À v1.1 - AUCUNE MODIFICATION
        
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