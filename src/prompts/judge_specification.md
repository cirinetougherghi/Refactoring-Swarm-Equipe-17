# 🧪 Spécification de l'Agent Testeur (Judge)

**Créé par :** Ingénieur Prompt  
**Date :** 10/01/2026  
**Version :** 1.0

---

## 🎯 Mission Principale

L'Agent Testeur est le **troisième agent** du système Refactoring Swarm.

**Sa mission :**
> Analyser les résultats de pytest (sortie console) et décider si le code corrigé est valide (VALIDATE) ou s'il nécessite une nouvelle correction (PASS_TO_FIXER).

---

## 📥 Entrées

Le Testeur reçoit :
1. **Nom du fichier testé** (exemple : `buggy_code.py`)
2. **Sortie console de pytest** (texte brut avec résultats des tests)

**Exemple d'entrée - Tests réussis :**
```
============================= test session starts ==============================
collected 3 items

test_code.py::test_calculate_average PASSED                              [ 33%]
test_code.py::test_process_data PASSED                                   [ 66%]
test_code.py::test_multiply_by_two PASSED                                [100%]

============================== 3 passed in 0.05s ===============================
```

**Exemple d'entrée - Tests échoués :**
```
============================= test session starts ==============================
collected 3 items

test_code.py::test_calculate_average PASSED                              [ 33%]
test_code.py::test_process_data FAILED                                   [ 66%]
test_code.py::test_multiply_by_two PASSED                                [100%]

=================================== FAILURES ===================================
__________________________ test_process_data ___________________________
    def test_process_data():
>       assert result == 3.0
E       assert 2.5 == 3.0

test_code.py:15: AssertionError
========================= 1 failed, 2 passed in 0.08s ==========================
```

---

## 📤 Sortie

Le Testeur produit un **objet JSON** avec cette structure :

**Cas 1 : Tous les tests passent**
```json
{
  "file": "buggy_code.py",
  "decision": "VALIDATE",
  "total_tests": 3,
  "passed": 3,
  "failed": 0,
  "errors": [],
  "message": "All tests passed successfully. Code is validated."
}
```

**Cas 2 : Au moins un test échoue**
```json
{
  "file": "buggy_code.py",
  "decision": "PASS_TO_FIXER",
  "total_tests": 3,
  "passed": 2,
  "failed": 1,
  "errors": [
    {
      "test_name": "test_process_data",
      "error_type": "AssertionError",
      "message": "assert 2.5 == 3.0",
      "location": "test_code.py:15"
    }
  ],
  "message": "1 test failed. Code needs correction."
}
```

**Cas 3 : Erreur d'exécution**
```json
{
  "file": "buggy_code.py",
  "decision": "PASS_TO_FIXER",
  "total_tests": 0,
  "passed": 0,
  "failed": 0,
  "errors": [
    {
      "test_name": "N/A",
      "error_type": "ImportError",
      "message": "No module named 'math'",
      "location": "buggy_code.py:2"
    }
  ],
  "message": "Execution error. Code cannot be tested."
}
```

---

## 🔍 Règles de Décision

### **VALIDATE - Code accepté**
**Conditions :**
- ✅ Tous les tests sont passés (100%)
- ✅ Aucune erreur d'exécution
- ✅ `pytest` s'est exécuté sans problème

**Action :** Le code est validé, fin du workflow

---

### **PASS_TO_FIXER - Renvoyer au Correcteur**
**Conditions :**
- ❌ Au moins 1 test échoue
- ❌ Erreur d'exécution (ImportError, SyntaxError, etc.)
- ❌ Aucun test n'a été collecté
- ❌ `pytest` n'a pas pu s'exécuter

**Action :** Renvoyer le code au Correcteur avec les logs d'erreur

---

## 🧪 Types de Résultats Pytest

### **1. Tests réussis (PASSED)**
```
test_code.py::test_function PASSED                                    [100%]
```
**Interprétation :** Test validé ✅

### **2. Tests échoués (FAILED)**
```
test_code.py::test_function FAILED                                    [100%]
E       assert 5 == 10
```
**Interprétation :** Assertion non respectée ❌

### **3. Erreurs d'exécution (ERROR)**
```
test_code.py::test_function ERROR                                     [100%]
E       ImportError: No module named 'math'
```
**Interprétation :** Code ne peut pas s'exécuter ❌

### **4. Tests ignorés (SKIPPED)**
```
test_code.py::test_function SKIPPED                                   [100%]
```
**Interprétation :** Test non exécuté (à traiter comme neutre)

---

## 📊 Extraction des Statistiques

### **Ligne de résumé pytest :**
```
====== 5 passed, 2 failed, 1 skipped in 0.12s ======
```

**Extraction :**
- `total_tests` = 5 + 2 = 7 (passés + échoués)
- `passed` = 5
- `failed` = 2
- `skipped` = 1 (optionnel)

---

## ✅ Ce que le Testeur DOIT faire

1. ✅ **Parser correctement** la sortie pytest (texte brut)
2. ✅ **Extraire les statistiques** (passed, failed, errors)
3. ✅ **Identifier les erreurs** avec noms de tests et messages
4. ✅ **Décider correctement** (VALIDATE ou PASS_TO_FIXER)
5. ✅ **Produire du JSON valide** uniquement
6. ✅ **Fournir des informations utiles** pour le Correcteur

---

## ❌ Ce que le Testeur NE DOIT PAS faire

1. ❌ **Ne PAS inventer** de résultats de tests
2. ❌ **Ne PAS ajouter** de texte avant/après le JSON
3. ❌ **Ne PAS corriger** le code (c'est le rôle du Correcteur)
4. ❌ **Ne PAS ignorer** les erreurs d'exécution
5. ❌ **Ne PAS valider** si au moins 1 test échoue

---

## 🎯 Critères de Succès

Le Testeur est réussi si :
- ✅ Parse correctement tous les formats de sortie pytest
- ✅ Décision toujours correcte (VALIDATE ou PASS_TO_FIXER)
- ✅ Statistiques exactes
- ✅ Erreurs bien extraites et formatées
- ✅ JSON toujours valide
- ✅ Pas de texte superflu

---

## 🔄 Interface avec les Autres Agents

### **Depuis l'Agent Correcteur**
Le Testeur reçoit le code corrigé et les résultats de pytest.

### **Vers l'Agent Correcteur (si PASS_TO_FIXER)**
Le Testeur renvoie les logs d'erreur pour une nouvelle correction.

### **Vers l'Orchestrateur (si VALIDATE)**
Le Testeur signale que le code est validé, fin du workflow.

---

## 🧪 Cas de Test

### **Cas 1 : Tous les tests passent**
**Sortie pytest :**
```
====== 3 passed in 0.05s ======
```
**Décision attendue :** `VALIDATE`

### **Cas 2 : Quelques tests échouent**
**Sortie pytest :**
```
====== 2 passed, 1 failed in 0.08s ======
```
**Décision attendue :** `PASS_TO_FIXER`

### **Cas 3 : Erreur d'exécution**
**Sortie pytest :**
```
E   ImportError: No module named 'math'
```
**Décision attendue :** `PASS_TO_FIXER`

### **Cas 4 : Aucun test collecté**
**Sortie pytest :**
```
====== no tests ran in 0.01s ======
```
**Décision attendue :** `PASS_TO_FIXER` (suspect)

---

**Cette spécification sera utilisée pour :**
1. Rédiger le prompt système du Testeur
2. Créer les fonctions Python d'analyse pytest
3. Valider que les décisions sont correctes