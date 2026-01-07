# Schéma de Logging - Refactoring Swarm
   
   ## Structure Obligatoire
   
   ### Champs Racine
   - `id` (string) : UUID unique
   - `timestamp` (ISO 8601) : Date/heure de l'action
   - `agent` (string) : Nom de l'agent
   - `model` (string) : Modèle LLM utilisé
   - `action` (ActionType) : Type d'action
   - `details` (dict) : Détails spécifiques
   - `status` (string) : "SUCCESS" ou "FAILURE"
   
   ### Champs Obligatoires dans `details`
   - `input_prompt` (string) : Prompt envoyé au LLM
   - `output_response` (string) : Réponse reçue du LLM
   
   ### Types d'Actions (ActionType)
   - `CODE_ANALYSIS` : Audit, lecture, recherche de bugs
   - `CODE_GEN` : Création de nouveau code/tests/docs
   - `DEBUG` : Analyse d'erreurs d'exécution
   - `FIX` : Application de correctifs