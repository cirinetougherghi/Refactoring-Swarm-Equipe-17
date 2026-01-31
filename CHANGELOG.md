# Changelog - The Refactoring Swarm

## [2.0.0] - 2026-01-31 - Migration LangGraph

### Changed
- Migration de la boucle while vers LangGraph pour l'orchestration
- Architecture déclarative du workflow multi-agents
- Meilleure traçabilité du flux d'exécution

### Added
- Nouveau fichier `src/workflow_graph.py` (graphe d'exécution)
- Champ `workflow_engine: "LangGraph_v2.0"` dans les logs
- Tests de validation du graphe (`test_graph.py`)

### Preserved
- Logique métier 100% identique à la version 1.1
- Compatibilité totale avec l'API existante
- Point d'entrée `main.py` inchangé
- Format des logs respecté

### Technical Details
- **Agents** : AuditorAgent, FixerAgent, JudgeAgent (inchangés)
- **Workflow Engine** : LangGraph v0.0.25
- **Nodes** : audit, fixer, judge_clean_code, judge_after_fix, validate, fail
- **Max Iterations** : Configurable via `--max_iterations`

---

## [1.1.0] - 2026-01-10 - Version initiale

### Added
- Système multi-agents avec orchestrateur
- Boucle while pour gestion des itérations
- Logging scientifique (experiment_data.json)