"""
Graphe d'exécution LangGraph pour le Refactoring Swarm
ATTENTION : Ce graphe respecte EXACTEMENT la logique de l'orchestrateur original
Ne pas modifier sans synchroniser avec l'équipe

Responsable : Lead Dev (Orchestrateur)
Date : 2026-01-31
Version : 2.0 - LangGraph Implementation (Logique identique à v1.1)
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
import operator

from src.agents import AuditorAgent, FixerAgent, JudgeAgent
from src.tools.file_tools import read_file


class RefactoringState(TypedDict):
    """
    État partagé entre tous les nœuds du graphe.
    Structure identique à WorkflowState de l'orchestrateur original.
    """
    file_path: str
    file_name: str
    iteration: Annotated[int, operator.add]
    max_iterations: int
    audit_report: dict
    judge_report: dict
    status: Literal["PENDING", "VALIDATED", "FAILED", "MAX_ITERATIONS"]
    total_bugs_found: Annotated[int, operator.add]
    total_bugs_fixed: Annotated[int, operator.add]
    original_code: str
    current_code: str


# ═══════════════════════════════════════════════════════════════
#  NŒUD 1 : AUDITOR (Analyse)
#  Logique identique : lignes 166-179 de l'orchestrateur original
# ═══════════════════════════════════════════════════════════════

def audit_node(state: RefactoringState) -> RefactoringState:
    """
    Nœud AUDITOR : Analyse le code et détecte les problèmes.
    
    LOGIQUE ORIGINALE (orchestrator.py lignes 166-179) :
        audit_report = self.auditor.analyze_file(file_path)
        if audit_report is None:
            state.status = "FAILED"
            break
        bugs_found = audit_report.get("total_issues", 0)
        state.total_bugs_found += bugs_found
    """
    print(f"\n{'='*80}")
    print(f"ITERATION {state['iteration'] + 1}/{state['max_iterations']}")
    print(f"{'='*80}")
    
    auditor = AuditorAgent()
    audit_report = auditor.analyze_file(state["file_path"])
    
    # EXACTEMENT comme ligne 170 : if audit_report is None
    if audit_report is None:
        print(f"ERREUR: Audit echoue - Arret du traitement")
        return {
            **state,
            "audit_report": {},
            "status": "FAILED",
            "iteration": 1
        }
    
    # EXACTEMENT comme lignes 175-176
    bugs_found = audit_report.get("total_issues", 0)
    
    return {
        **state,
        "audit_report": audit_report,
        "total_bugs_found": bugs_found,
        "iteration": 1
    }


# ═══════════════════════════════════════════════════════════════
#  DÉCISION APRÈS AUDIT : Code propre ?
#  Logique identique : lignes 178-193 de l'orchestrateur original
# ═══════════════════════════════════════════════════════════════

def route_after_audit(state: RefactoringState) -> Literal["judge_clean_code", "fixer", "end"]:
    """
    Route après l'audit selon le nombre de bugs.
    
    LOGIQUE ORIGINALE (orchestrator.py lignes 178-193) :
        if bugs_found == 0:
            judge_report = self.judge.judge_file(file_path, audit_report)
            if judge_report.get("decision") == "VALIDATE":
                status = "VALIDATED"
                break
            else:
                status = "FAILED"
                break
    """
    # Si l'audit a échoué, on arrête
    if state["status"] == "FAILED":
        return "end"
    
    bugs_found = state.get("audit_report", {}).get("total_issues", 0)
    
    # EXACTEMENT comme ligne 178 : if bugs_found == 0
    if bugs_found == 0:
        print(f"Code propre - Aucun bug detecte")
        return "judge_clean_code"
    
    # Sinon, on passe au FIXER
    return "fixer"


# ═══════════════════════════════════════════════════════════════
#  NŒUD 2 : JUDGE (pour code propre uniquement)
#  Logique identique : lignes 181-193 de l'orchestrateur original
# ═══════════════════════════════════════════════════════════════

def judge_clean_code_node(state: RefactoringState) -> RefactoringState:
    """
    Nœud JUDGE pour code propre (0 bugs détectés).
    
    LOGIQUE ORIGINALE (orchestrator.py lignes 181-193) :
        judge_report = self.judge.judge_file(file_path, audit_report)
        if judge_report.get("decision") == "VALIDATE":
            state.status = "VALIDATED"
            self.files_validated += 1
            break
        else:
            state.status = "FAILED"
            break
    """
    judge = JudgeAgent()
    
    # EXACTEMENT comme ligne 182 : Passer audit_report au judge
    judge_report = judge.judge_file(state["file_path"], state["audit_report"])
    
    # EXACTEMENT comme ligne 184
    if judge_report and judge_report.get("decision") == "VALIDATE":
        print(f"\n✅ {state['file_name']} VALIDE !")
        return {
            **state,
            "judge_report": judge_report,
            "status": "VALIDATED"
        }
    else:
        # EXACTEMENT comme lignes 189-191
        print(f"ATTENTION: Tests ont echoue malgre l'absence de bugs detectes")
        return {
            **state,
            "judge_report": judge_report if judge_report else {},
            "status": "FAILED"
        }


# ═══════════════════════════════════════════════════════════════
#  NŒUD 3 : FIXER (Correction)
#  Logique identique : lignes 195-201 de l'orchestrateur original
# ═══════════════════════════════════════════════════════════════

def fixer_node(state: RefactoringState) -> RefactoringState:
    """
    Nœud FIXER : Corrige les bugs selon le rapport d'audit.
    
    LOGIQUE ORIGINALE (orchestrator.py lignes 195-201) :
        fix_success = self.fixer.fix_file(file_path, audit_report)
        if not fix_success:
            state.status = "FAILED"
            break
        state.current_code = read_file(file_path)
        state.total_bugs_fixed += bugs_found
    """
    fixer = FixerAgent()
    
    # EXACTEMENT comme ligne 196
    fix_success = fixer.fix_file(state["file_path"], state["audit_report"])
    
    # EXACTEMENT comme ligne 198
    if not fix_success:
        print(f"ERREUR: Correction echouee - Arret du traitement")
        return {
            **state,
            "status": "FAILED"
        }
    
    # EXACTEMENT comme ligne 202
    try:
        current_code = read_file(state["file_path"])
    except Exception as e:
        print(f"ERREUR: Impossible de lire le fichier corrigé : {e}")
        return {
            **state,
            "status": "FAILED"
        }
    
    # EXACTEMENT comme ligne 203
    bugs_fixed = state["audit_report"].get("total_issues", 0)
    
    return {
        **state,
        "current_code": current_code,
        "total_bugs_fixed": bugs_fixed
    }


# ═══════════════════════════════════════════════════════════════
#  NŒUD 4 : JUDGE (après FIX)
#  Logique identique : lignes 205-228 de l'orchestrateur original
# ═══════════════════════════════════════════════════════════════

def judge_after_fix_node(state: RefactoringState) -> RefactoringState:
    """
    Nœud JUDGE après correction.
    
    LOGIQUE ORIGINALE (orchestrator.py lignes 205-228) :
        judge_report = self.judge.judge_file(file_path, audit_report)
        if judge_report is None:
            state.status = "FAILED"
            break
        decision = judge_report.get("decision")
        if decision == "VALIDATE":
            status = "VALIDATED"
            break
        elif decision == "PASS_TO_FIXER":
            continue
        else:
            status = "FAILED"
            break
    """
    judge = JudgeAgent()
    
    # EXACTEMENT comme ligne 207 : Passer audit_report
    judge_report = judge.judge_file(state["file_path"], state["audit_report"])
    
    # EXACTEMENT comme ligne 209
    if judge_report is None:
        print(f"ERREUR: Test echoue - Arret du traitement")
        return {
            **state,
            "judge_report": {},
            "status": "FAILED"
        }
    
    return {
        **state,
        "judge_report": judge_report
    }


# ═══════════════════════════════════════════════════════════════
#  DÉCISION APRÈS JUDGE : Valider, réessayer ou échouer ?
#  Logique identique : lignes 215-228 de l'orchestrateur original
# ═══════════════════════════════════════════════════════════════

def route_after_judge(state: RefactoringState) -> Literal["validate", "retry_audit", "fail"]:
    """
    Détermine la suite après le test.
    
    LOGIQUE ORIGINALE (orchestrator.py lignes 215-228) :
        decision = judge_report.get("decision")
        if decision == "VALIDATE":
            status = "VALIDATED"
            break
        elif decision == "PASS_TO_FIXER":
            if iteration >= max_iterations:
                status = "MAX_ITERATIONS"
                break
            continue
        else:
            status = "FAILED"
            break
    """
    # Si déjà en échec
    if state["status"] == "FAILED":
        return "fail"
    
    # EXACTEMENT comme ligne 215
    decision = state.get("judge_report", {}).get("decision")
    
    # EXACTEMENT comme ligne 217
    if decision == "VALIDATE":
        print(f"\n✅ {state['file_name']} VALIDE !")
        return "validate"
    
    # EXACTEMENT comme ligne 221
    elif decision == "PASS_TO_FIXER":
        # EXACTEMENT comme ligne 222
        print(f"\nATTENTION: Tests echoues - Nouvelle iteration necessaire")
        
        # EXACTEMENT comme ligne 224
        if state["iteration"] >= state["max_iterations"]:
            print(f"\nATTENTION: Limite de {state['max_iterations']} iterations atteinte")
            return "fail"
        
        # EXACTEMENT comme ligne 228 : continue (nouvelle itération)
        return "retry_audit"
    
    # EXACTEMENT comme ligne 230
    else:
        print(f"ERREUR: Decision inconnue du Judge : {decision}")
        return "fail"


# ═══════════════════════════════════════════════════════════════
#  NŒUDS FINAUX : VALIDATE et FAIL
# ═══════════════════════════════════════════════════════════════

def validate_node(state: RefactoringState) -> RefactoringState:
    """
    Nœud final : Validation réussie.
    
    LOGIQUE ORIGINALE : Correspond aux lignes 217-220 et 185-187
    """
    return {
        **state,
        "status": "VALIDATED"
    }


def fail_node(state: RefactoringState) -> RefactoringState:
    """
    Nœud final : Échec.
    
    LOGIQUE ORIGINALE : Correspond aux différents cas d'échec
    """
    # EXACTEMENT comme ligne 225
    if state["iteration"] >= state["max_iterations"]:
        return {
            **state,
            "status": "MAX_ITERATIONS"
        }
    
    return {
        **state,
        "status": "FAILED"
    }


# ═══════════════════════════════════════════════════════════════
#  CONSTRUCTION DU GRAPHE
#  Reproduit exactement le flux de l'orchestrateur original
# ═══════════════════════════════════════════════════════════════

def create_refactoring_graph() -> StateGraph:
    """
    Crée le graphe LangGraph qui reproduit EXACTEMENT la logique
    de la boucle while de l'orchestrateur original (lignes 164-232).
    
    FLUX ORIGINAL :
        while iteration < max_iterations:
            iteration += 1
            
            # AUDIT
            audit_report = auditor.analyze_file()
            if audit_report is None: break (FAILED)
            
            bugs_found = audit_report.get("total_issues", 0)
            
            # Si code propre
            if bugs_found == 0:
                judge_report = judge.judge_file()
                if decision == "VALIDATE": break (VALIDATED)
                else: break (FAILED)
            
            # Si bugs détectés
            fix_success = fixer.fix_file()
            if not fix_success: break (FAILED)
            
            judge_report = judge.judge_file()
            if judge_report is None: break (FAILED)
            
            decision = judge_report.get("decision")
            if decision == "VALIDATE": break (VALIDATED)
            elif decision == "PASS_TO_FIXER": continue (RETRY)
            else: break (FAILED)
    """
    print("\n🏗️  Construction du graphe LangGraph (logique v1.1)...")
    
    workflow = StateGraph(RefactoringState)
    
    # Ajout des nœuds
    workflow.add_node("audit", audit_node)
    workflow.add_node("judge_clean_code", judge_clean_code_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("judge_after_fix", judge_after_fix_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("fail", fail_node)
    
    # Point d'entrée : AUDIT (comme ligne 166)
    workflow.set_entry_point("audit")
    
    # Après AUDIT : bugs == 0 ? → JUDGE_CLEAN_CODE, sinon → FIXER
    # (comme lignes 178-193 vs 195+)
    workflow.add_conditional_edges(
        "audit",
        route_after_audit,
        {
            "judge_clean_code": "judge_clean_code",
            "fixer": "fixer",
            "end": "fail"
        }
    )
    
    # Après JUDGE_CLEAN_CODE : VALIDATE ou FAIL (comme lignes 184-191)
    workflow.add_conditional_edges(
        "judge_clean_code",
        lambda state: "validate" if state["status"] == "VALIDATED" else "fail",
        {
            "validate": "validate",
            "fail": "fail"
        }
    )
    
    # Après FIXER : JUDGE_AFTER_FIX (comme ligne 205)
    workflow.add_edge("fixer", "judge_after_fix")
    
    # Après JUDGE_AFTER_FIX : VALIDATE, RETRY ou FAIL
    # (comme lignes 215-231)
    workflow.add_conditional_edges(
        "judge_after_fix",
        route_after_judge,
        {
            "validate": "validate",
            "retry_audit": "audit",  # Continue (comme ligne 228)
            "fail": "fail"
        }
    )
    
    # Nœuds finaux
    workflow.add_edge("validate", END)
    workflow.add_edge("fail", END)
    
    app = workflow.compile()
    
    print("✅ Graphe LangGraph créé (logique identique à v1.1) !\n")
    
    return app


# Instance globale (à importer dans orchestrator.py)
refactoring_graph = create_refactoring_graph()