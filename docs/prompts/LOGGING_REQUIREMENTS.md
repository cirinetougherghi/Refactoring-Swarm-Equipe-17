# 📊 Exigences de Logging - Module de Prompts

**Auteur** : Ingénieur Prompt  
**Date** : 11/01/2026  
**Destinataire** : Data Officer  

---

## 🎯 Vue d'Ensemble

Le module de prompts génère **3 types d'interactions** avec le LLM qui doivent être loggées.

---

## 📋 ActionType par Agent

| Agent | ActionType | Justification |
|-------|------------|---------------|
| **Auditeur** | `ActionType.ANALYSIS` | Analyse le code pour détecter les bugs |
| **Correcteur** | `ActionType.FIX` | Corrige les bugs identifiés |
| **Testeur** | `ActionType.DEBUG` | Analyse les résultats des tests |

---

## 📊 Format des Logs

### Agent Auditeur
```python
log_experiment(
    agent_name="Auditor",
    model_used="gemini-2.5-flash",
    action=ActionType.ANALYSIS,
    details={
        "file_analyzed": "buggy_code.py",
        "input_prompt": "Tu es un expert Python...",  # ← PROMPT COMPLET
        "output_response": '{"file":"buggy_code.py",...}',  # ← RÉPONSE BRUTE
        "issues_found": 5,
        "severity_breakdown": {
            "high": 2,
            "medium": 2,
            "low": 1
        }
    },
    status="SUCCESS"
)
```

### Agent Correcteur
```python
log_experiment(
    agent_name="Fixer",
    model_used="gemini-2.5-flash",
    action=ActionType.FIX,
    details={
        "file_fixed": "buggy_code.py",
        "input_prompt": "Tu dois corriger ce code...",  # ← PROMPT COMPLET
        "output_response": "def calculate(x, y):\n...",  # ← CODE CORRIGÉ
        "bugs_corrected": 5,
        "code_length_before": 150,
        "code_length_after": 180
    },
    status="SUCCESS"
)
```

### Agent Testeur
```python
log_experiment(
    agent_name="Judge",
    model_used="gemini-2.5-flash",
    action=ActionType.DEBUG,
    details={
        "file_tested": "fixed_code.py",
        "input_prompt": "Analyse ces résultats pytest...",  # ← PROMPT COMPLET
        "output_response": '{"decision":"VALIDATE",...}',  # ← DÉCISION JSON
        "decision": "VALIDATE",
        "tests_passed": 10,
        "tests_failed": 0
    },
    status="SUCCESS"
)
```

---

## ✅ Champs OBLIGATOIRES

Chaque log **DOIT** contenir :

1. ✅ `agent_name` (string)
2. ✅ `model_used` (string) → toujours "gemini-2.5-flash"
3. ✅ `action` (ActionType Enum) → ANALYSIS, FIX, ou DEBUG
4. ✅ `details` (dict) contenant :
   - ✅ `input_prompt` (string) → **PROMPT COMPLET ENVOYÉ AU LLM**
   - ✅ `output_response` (string) → **RÉPONSE BRUTE DU LLM**
5. ✅ `status` (string) → "SUCCESS" ou "FAILED"

---

## ⚠️ Points Critiques

### 1. `input_prompt` et `output_response` sont OBLIGATOIRES

Sans ces champs, impossible d'analyser :
- La qualité des prompts
- Le coût en tokens
- Les patterns de réponse du LLM

### 2. Toujours utiliser l'Enum `ActionType`

❌ **MAUVAIS** :
```python
action="analysis"  # String
```

✅ **BON** :
```python
from src.utils.logger import ActionType
action=ActionType.ANALYSIS  # Enum
```

### 3. Logger même en cas d'erreur
```python
try:
    response = model.generate_content(prompt)
    # ... traitement ...
    log_experiment(..., status="SUCCESS")
except Exception as e:
    log_experiment(
        agent_name="Auditor",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": prompt,
            "error": str(e)
        },
        status="FAILED"
    )
```

---

## 📊 Exemple de Log Final (JSON)
```json
{
  "timestamp": "2026-01-11T14:30:00",
  "agent_name": "Auditor",
  "model_used": "gemini-2.5-flash",
  "action": "ANALYSIS",
  "details": {
    "file_analyzed": "buggy_code.py",
    "input_prompt": "Tu es un expert Python. Analyse ce code...",
    "output_response": "{\"file\":\"buggy_code.py\",\"total_issues\":5,...}",
    "issues_found": 5
  },
  "status": "SUCCESS"
}
```

---

## ✅ Validation

Le module de prompts a été testé avec le logger :
- ✅ Tous les champs obligatoires présents
- ✅ `ActionType` correctement utilisé
- ✅ `input_prompt` et `output_response` capturés
- ✅ Format JSON valide

---

## 📞 Questions pour le Data Officer

1. Le format ci-dessus est-il conforme ?
2. Y a-t-il d'autres champs à ajouter dans `details` ?
3. Comment gérer les prompts très longs (>10000 caractères) ?
4. Faut-il logger les tentatives échouées (retry) ?

---

**Prêt pour validation ! ✅**