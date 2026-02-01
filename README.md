## 🏗️ Architecture Technique

### Workflow Engine : LangGraph

Le système utilise **LangGraph v0.0.25** pour orchestrer les agents :

**Avantages** :
- ✅ Graphe déclaratif (vs boucle impérative)
- ✅ Meilleure traçabilité du flux d'exécution
- ✅ Extensibilité pour ajout de nouveaux agents
- ✅ Gestion automatique des transitions d'état

**Logique préservée** :
- ✅ Flux identique à 100% avec la version 1.1
- ✅ Validation par comparaison des logs
- ✅ Tous les tests passent

### Graphe d'exécution
```
START → AUDIT → [Code propre ?]
                ├─ OUI → JUDGE_CLEAN_CODE → [Validé ?]
                │                          ├─ OUI → VALIDATE → END
                │                          └─ NON → FAIL → END
                └─ NON → FIXER → JUDGE_AFTER_FIX → [Décision ?]
                                                   ├─ VALIDATE → END
                                                   ├─ RETRY → AUDIT (boucle)
                                                   └─ FAIL → END
 ## 🏗️ Architecture : Graphe d'Exécution LangGraph

### Diagramme du Workflow
```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────────┐
│    AUDIT    │ (Analyse du code)
└──────┬──────┘
       │
       ├──[Bugs détectés ?]
       │
       ├─ OUI ─────────────────────────────────┐
       │                                        │
       │                                        ▼
       │                                  ┌──────────┐
       │                                  │  FIXER   │ (Corrige les bugs)
       │                                  └─────┬────┘
       │                                        │
       │                                        ▼
       │                                  ┌───────────────────┐
       │                                  │ JUDGE_AFTER_FIX   │ (Teste après correction)
       │                                  └─────┬─────────────┘
       │                                        │
       │                                        ├──[Décision ?]
       │                                        │
       │                                        ├─ VALIDATE ──────┐
       │                                        │                  │
       │                                        ├─ PASS_TO_FIXER ─┼─ (Retour vers AUDIT si < max_iterations)
       │                                        │                  │
       │                                        └─ FAIL ──────────┼──┐
       │                                                           │  │
       └─ NON ──────────────┐                                     │  │
                             │                                     │  │
                             ▼                                     │  │
                       ┌──────────────────┐                       │  │
                       │ JUDGE_CLEAN_CODE │ (Valide code propre)  │  │
                       └────────┬─────────┘                       │  │
                                │                                  │  │
                                ├──[Validé ?]                      │  │
                                │                                  │  │
                                ├─ OUI ──────────────────────────┐│  │
                                │                                 ││  │
                                └─ NON ─────────────────────────┐││  │
                                                                 │││  │
                                                                 ▼▼▼  ▼
                                                              ┌──────────┐
                                                              │ VALIDATE │
                                                              └─────┬────┘
                                                                    │
                                                                    ▼
                                                                ┌───────┐
                                                                │  END  │
                                                                └───────┘
                                                                    ▲
                                                                    │
                                                              ┌─────┴────┐
                                                              │   FAIL   │
                                                              └──────────┘
```

### Nœuds du Graphe

| Nœud | Rôle | Agent responsable |
|------|------|-------------------|
| **AUDIT** | Analyse du code, détecte les bugs | AuditorAgent |
| **FIXER** | Corrige les bugs détectés | FixerAgent |
| **JUDGE_CLEAN_CODE** | Valide du code sans bugs | JudgeAgent |
| **JUDGE_AFTER_FIX** | Teste après correction | JudgeAgent |
| **VALIDATE** | État final de succès | - |
| **FAIL** | État final d'échec | - |

### Arêtes du Graphe

| Source | Destination | Condition |
|--------|-------------|-----------|
| START | AUDIT | Toujours |
| AUDIT | JUDGE_CLEAN_CODE | `bugs_detected == 0` |
| AUDIT | FIXER | `bugs_detected > 0` |
| FIXER | JUDGE_AFTER_FIX | Toujours |
| JUDGE_CLEAN_CODE | VALIDATE | Décision = "VALIDATE" |
| JUDGE_CLEAN_CODE | FAIL | Décision ≠ "VALIDATE" |
| JUDGE_AFTER_FIX | VALIDATE | Décision = "VALIDATE" |
| JUDGE_AFTER_FIX | AUDIT | Décision = "PASS_TO_FIXER" ET `iteration < max_iterations` |
| JUDGE_AFTER_FIX | FAIL | Autre cas |
| VALIDATE | END | Toujours |
| FAIL | END | Toujours |

### Implémentation Technique

- **Framework** : LangGraph v0.0.25
- **Type de graphe** : `StateGraph` (graphe orienté avec état partagé)
- **État partagé** : `RefactoringState` (TypedDict)
- **Transitions** : Conditionnelles (`add_conditional_edges`) et directes (`add_edge`)
```