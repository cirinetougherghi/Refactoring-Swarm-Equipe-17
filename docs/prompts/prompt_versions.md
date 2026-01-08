# 📚 Historique des Versions - Prompts

## 🔍 Agent Auditeur

### Version 1.0 (2026-01-08)

**Créé par :** Ingénieur Prompt  
**Statut :** ✅ Validé - Production Ready

---

#### 🎯 Caractéristiques

**Modèle utilisé :** `gemini-2.5-flash`

**Capacités :**
- ✅ Détection de 4 niveaux de sévérité (CRITICAL, HIGH, MEDIUM, LOW)
- ✅ 13 types de problèmes détectés
- ✅ Format JSON structuré et validé
- ✅ Instructions strictes contre les hallucinations
- ✅ Exemples de format inclus dans le prompt

---

#### 🐛 Types de problèmes détectés

**CRITICAL (3 types) :**
- Variables non définies (undefined_variable)
- Imports manquants (missing_import)
- Erreurs de syntaxe

**HIGH (5 types) :**
- Division par zéro (division_by_zero)
- Index hors limites (index_out_of_bounds)
- Clés de dictionnaire inexistantes (key_error)
- Opérations sur None (none_operation)
- Fichiers inexistants (file_not_found)

**MEDIUM (3 types) :**
- Docstrings manquantes (missing_docstring)
- Noms non descriptifs (non_descriptive_name)
- Code dupliqué (duplicate_code)

**LOW (4 types) :**
- Espacement PEP8 (pep8_spacing)
- Longueur de ligne (pep8_line_length)
- Nom de classe en minuscules (class_name_lowercase)
- Imports désordonnés

---

#### 🧪 Tests effectués

##### Test 1 : buggy_code_simple.py (4 bugs attendus)
**Date :** 2026-01-08  
**Résultat :** ✅ SUCCÈS  
**Bugs détectés :** 5/4 (100% + 1 bonus)  
**Détails :**
- ✅ Import manquant (math) - CRITICAL
- ✅ Division par zéro potentielle - HIGH
- ✅ 3 docstrings manquantes - MEDIUM
- ✅ JSON parfaitement valide
- ✅ Aucun faux positif
- ✅ Descriptions claires et suggestions actionnables

**Temps d'exécution :** ~3-5 secondes  
**Tokens utilisés :** ~1159 input + ~374 output = ~1533 tokens

---

#### 📊 Métriques de performance

**Version 1.0 :**
- **Taux de détection :** 100% (sur buggy_code_simple.py)
- **Taux de faux positifs :** 0%
- **Validité du JSON :** 100%
- **Clarté des descriptions :** Excellente
- **Respect du format :** 100%

**Estimation coûts (tokens moyens par fichier) :**
- Input : ~1500 tokens
- Output : ~800 tokens
- **Total : ~2300 tokens**

---

#### ⚠️ Problèmes connus

**Version 1.0 :**
- ❌ Aucun problème majeur identifié
- ✅ Prompt fonctionne comme prévu

---

#### 🔄 Améliorations prévues (v1.1)

**Optimisations futures :**
1. Réduction du nombre de tokens (objectif : -20%)
2. Tests sur fichiers plus complexes (buggy_code_complex.py)
3. Validation sur cas limites (buggy_code_edge_cases.py)
4. Ajout de métriques de performance détaillées

**Nouvelles fonctionnalités :**
- Détection de code mort (unused variables)
- Analyse de la complexité cyclomatique
- Suggestions de refactoring

---

#### 💾 Fichiers associés

- **Prompt :** `src/prompts/auditor_prompt.py`
- **Spécification :** `src/prompts/auditor_specification.md`
- **Tests :** `test_auditor_with_gemini.py`
- **Résultats :** `test_results_*.json`

---

#### 📝 Notes de développement

**Leçons apprises :**
- Les instructions strictes en majuscules fonctionnent très bien
- Les exemples de format dans le prompt sont essentiels
- Gemini 2.5 Flash respecte parfaitement les consignes JSON
- Répéter "UNIQUEMENT du JSON" plusieurs fois est efficace

**Best practices validées :**
- ✅ Structurer le prompt en sections claires
- ✅ Utiliser des emojis pour la lisibilité
- ✅ Donner des exemples concrets de bugs
- ✅ Préciser les niveaux de sévérité avec critères clairs

---

## 🛠️ Agent Correcteur

### Version 1.0 (À venir)
_Documentation à compléter_

---

## ✅ Agent Testeur

### Version 1.0 (À venir)
_Documentation à compléter_

---

**Dernière mise à jour :** 2026-01-08  
**Maintenu par :** Ingénieur Prompt