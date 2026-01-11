# 🤖 Module de Prompts - Refactoring Swarm

**Auteur** : Ingénieur Prompt  
**Version** : 1.0.0  
**Date** : 2026-01-11  
**Statut** : ✅ Validé et prêt pour l'intégration  

---

## 📋 Vue d'Ensemble

Ce module contient les **prompts système** (System Prompts) pour les trois agents spécialisés du Refactoring Swarm :

1. **🔍 Auditeur (Auditor)** - Analyse le code et détecte les problèmes
2. **🔧 Correcteur (Fixer)** - Corrige les bugs identifiés
3. **⚖️ Testeur (Judge)** - Valide les corrections via pytest

Chaque prompt a été optimisé pour :
- ✅ Minimiser les hallucinations
- ✅ Produire des sorties structurées (JSON)
- ✅ Réduire le coût en tokens
- ✅ Fonctionner avec Gemini 2.5 Flash

---

## 📂 Structure des Fichiers
```
src/prompts/
├── __init__.py              # Exports et métadonnées du module
├── auditor_prompt.py        # Prompt de l'Agent Auditeur
├── fixer_prompt.py          # Prompt de l'Agent Correcteur
├── judge_prompt.py          # Prompt de l'Agent Testeur
├── prompt_versions.md       # Historique des versions
└── README.md               # Ce fichier
```

### Fichiers Associés
```
tests/
├── test_auditor_comprehensive.py   # Tests de l'Auditeur
├── test_fixer_comprehensive.py     # Tests du Correcteur
└── test_judge_comprehensive.py     # Tests du Testeur

docs/prompts/
└── GUIDE_ORCHESTRATEUR.md         # Guide d'intégration
```

---

## 🚀 Guide d'Utilisation Rapide

### Installation
```python
# Le module est déjà installé si vous avez fait :
pip install -e .
```

### Import des Fonctions
```python
from src.prompts import (
    get_auditor_prompt,
    get_fixer_prompt,
    get_judge_prompt
)
```

### Exemple Complet : Workflow de Base
```python
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from src.prompts import get_auditor_prompt, get_fixer_prompt, get_judge_prompt

# Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# 1. AUDIT
filename = "buggy_code.py"
with open(filename, 'r') as f:
    code = f.read()

prompt = get_auditor_prompt(filename, code)
response = model.generate_content(prompt)
audit_report = json.loads(response.text)

print(f"🔍 Bugs détectés : {audit_report['total_issues']}")

# 2. CORRECTION
prompt = get_fixer_prompt(filename, code, audit_report)
response = model.generate_content(prompt)
fixed_code = response.text

print("🔧 Code corrigé généré")

# 3. VALIDATION
# (Exécuter pytest ici, puis analyser la sortie)
pytest_output = "... sortie de pytest ..."
prompt = get_judge_prompt(filename, pytest_output)
response = model.generate_content(prompt)
judge_decision = json.loads(response.text)

if judge_decision['decision'] == 'VALIDATE':
    print("✅ Mission réussie !")
else:
    print("🔄 Nouvelle itération nécessaire")
```

---

## 📊 Métriques de Performance

### Tokens et Coûts (Moyenne par Agent)

| Agent | Input Tokens | Output Tokens | Total | Temps Moyen |
|-------|--------------|---------------|-------|-------------|
| Auditeur | ~428 | ~667 | ~1095 | ~3s |
| Correcteur | ~996 | ~274 | ~1270 | ~4s |
| Testeur | ~271 | ~31 | ~302 | ~1s |
| **Workflow Complet** | - | - | **~2667** | **~8s** |

**Coût** : Gratuit avec Gemini 2.5 Flash (Free Tier)

### Taux de Réussite (Tests Validés)

| Agent | Tests Passés | Taux de Détection | Faux Positifs |
|-------|--------------|-------------------|---------------|
| Auditeur | 12/12 | 100% | 0% |
| Correcteur | __/__ | __% | __% |
| Testeur | __/__ | __% | __% |

---

## 📖 Documentation Détaillée

### Pour l'Orchestrateur
👉 **[Guide d'Intégration Complet](../../docs/prompts/GUIDE_ORCHESTRATEUR.md)**

Contient :
- Comment intégrer les prompts dans votre workflow
- Comment gérer les erreurs
- Comment logger les interactions
- Exemples de code complets

### Historique des Versions
👉 **[prompt_versions.md](./prompt_versions.md)**

Contient :
- Toutes les versions des prompts
- Changements entre versions
- Tests et validations
- Leçons apprises

---

## 🔧 API Reference

### `get_auditor_prompt(filename: str, code_content: str) -> str`

Génère le prompt pour l'Agent Auditeur.

**Paramètres :**
- `filename` (str) : Nom du fichier à analyser
- `code_content` (str) : Contenu du code Python à analyser

**Retourne :**
- `str` : Le prompt complet prêt à être envoyé à Gemini

**Exemple :**
```python
prompt = get_auditor_prompt("test.py", "def func():\n    x = undefined")
```

---

### `get_fixer_prompt(filename: str, code_content: str, audit_report: dict) -> str`

Génère le prompt pour l'Agent Correcteur.

**Paramètres :**
- `filename` (str) : Nom du fichier à corriger
- `code_content` (str) : Code original (buggé)
- `audit_report` (dict) : Rapport JSON de l'Auditeur

**Retourne :**
- `str` : Le prompt complet

**Exemple :**
```python
prompt = get_fixer_prompt("test.py", buggy_code, audit_report)
```

---

### `get_judge_prompt(filename: str, pytest_output: str) -> str`

Génère le prompt pour l'Agent Testeur.

**Paramètres :**
- `filename` (str) : Nom du fichier testé
- `pytest_output` (str) : Sortie console de pytest (texte brut)

**Retourne :**
- `str` : Le prompt complet

**Exemple :**
```python
prompt = get_judge_prompt("test.py", pytest_stdout)
```

---

## 🎯 Fonctions Utilitaires

### `get_module_info() -> dict`

Retourne les métadonnées complètes du module.
```python
from src.prompts import get_module_info

info = get_module_info()
print(info['version'])  # "1.0.0"
print(info['all_validated'])  # True
```

### `print_module_info() -> None`

Affiche un résumé formaté dans la console.
```python
from src.prompts import print_module_info

print_module_info()
# Affiche toutes les métriques et statuts
```

---

## ⚠️ Gestion des Erreurs

### Erreurs Courantes

#### 1. JSON Invalide dans la Réponse

**Problème :**
```python
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Solution :**
```python
import json

response_text = response.text.strip()

# Nettoyer les backticks markdown
if response_text.startswith("```json"):
    response_text = response_text[7:]
if response_text.endswith("```"):
    response_text = response_text[:-3]

response_text = response_text.strip()

try:
    data = json.loads(response_text)
except json.JSONDecodeError as e:
    print(f"Erreur de parsing : {e}")
    print(f"Réponse brute : {response_text[:200]}")
```

#### 2. Quota API Dépassé

**Problème :**
```
ResourceExhausted: 429 You exceeded your current quota
```

**Solution :**
```python
import time
from google.api_core import exceptions

try:
    response = model.generate_content(prompt)
except exceptions.ResourceExhausted as e:
    print("⏳ Quota dépassé, attente de 60 secondes...")
    time.sleep(60)
    response = model.generate_content(prompt)
```

#### 3. Prompt Trop Long

**Problème :**
```
InvalidArgument: Request payload size exceeds the limit
```

**Solution :**
- Réduire la taille du code à analyser
- Diviser en chunks plus petits
- Utiliser la version optimisée du prompt

---

## 📞 Contact & Support

### Responsable du Module
**Ingénieur Prompt** - Équipe Refactoring Swarm

### Signaler un Problème
1. Vérifier le [Guide de Troubleshooting](../../docs/prompts/GUIDE_ORCHESTRATEUR.md#troubleshooting)
2. Consulter l'[Historique des Versions](./prompt_versions.md)
3. Contacter l'Ingénieur Prompt via Discord/Slack

### Contribuer
- Les prompts sont versionnés dans `prompt_versions.md`
- Toute modification doit être testée avec la suite de tests
- Documenter les changements dans le fichier de versions

---

## 📜 Licence & Utilisation

Ce module fait partie du projet académique **Refactoring Swarm** (TP IGL 2025-2026).

**Usage** : Projet académique uniquement  
**Équipe** : Équipe 17  
**Enseignant** : BATATA Sofiane  
**École** : École Nationale Supérieure d'Informatique  

---

## 🔄 Changelog

### Version 1.0.0 (2026-01-11)
- ✅ Prompt Auditeur v1.0 validé (12/12 tests)
- ✅ Prompt Correcteur v1.0 (en cours de validation)
- ✅ Prompt Testeur v1.0 (en cours de validation)
- ✅ Optimisation tokens (-51.8% vs version initiale)
- ✅ Documentation complète
- ✅ Tests automatisés

---

**Dernière mise à jour** : 2026-01-11  
**Statut** : ✅ Prêt pour l'intégration avec l'Orchestrateur