# 🔧 Spécification de l'Agent Correcteur (Fixer)

**Créé par :** Ingénieur Prompt  
**Date :** 09/01/2026  
**Version :** 1.0

---

## 🎯 Mission Principale

L'Agent Correcteur est le **deuxième agent** du système Refactoring Swarm.

**Sa mission :**
> Lire le code Python buggé ET le rapport JSON de l'Auditeur, puis corriger TOUS les problèmes détectés en respectant la logique originale du code.

---

## 📥 Entrées

Le Correcteur reçoit :
1. **Nom du fichier** (exemple : `buggy_code.py`)
2. **Code original** (avec bugs)
3. **Rapport JSON de l'Auditeur** (liste structurée des problèmes)

**Exemple de rapport d'entrée :**
```json
{
  "file": "example.py",
  "total_issues": 3,
  "issues": [
    {
      "line": 5,
      "type": "missing_import",
      "severity": "CRITICAL",
      "description": "Module 'math' is used but not imported",
      "suggestion": "Add 'import math' at the beginning"
    },
    {
      "line": 10,
      "type": "missing_docstring",
      "severity": "MEDIUM",
      "description": "Function 'calculate' has no docstring",
      "suggestion": "Add a docstring"
    },
    {
      "line": 15,
      "type": "division_by_zero",
      "severity": "HIGH",
      "description": "Division by 'count' which can be zero",
      "suggestion": "Add check: if count == 0: return 0"
    }
  ]
}
```

---

## 📤 Sortie

Le Correcteur produit :
- **Code Python corrigé** (texte brut, pas de markdown)
- **RIEN D'AUTRE** (pas d'explications, pas de commentaires supplémentaires)

**Format de sortie :**
```python
import math

def calculate(numbers):
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers (list): List of numbers
        
    Returns:
        float: The average
    """
    if not numbers:
        return 0
    
    total = sum(numbers)
    count = len(numbers)
    
    if count == 0:
        return 0
    
    average = total / count
    return average
```

---

## 🔧 Types de Corrections à Effectuer

### **1. CRITICAL - Corrections immédiates**
- **Imports manquants** → Ajouter les imports nécessaires en haut du fichier
- **Variables non définies** → Définir les variables ou les passer en paramètres
- **Erreurs de syntaxe** → Corriger la syntaxe Python

### **2. HIGH - Protections contre les crashes**
- **Division par zéro** → Ajouter une vérification avant la division
- **Index hors limites** → Vérifier la taille de la liste avant l'accès
- **KeyError** → Utiliser `.get()` ou vérifier l'existence de la clé
- **Opérations sur None** → Ajouter des vérifications `if variable is not None:`
- **Fichiers inexistants** → Ajouter un try/except pour gérer l'erreur

### **3. MEDIUM - Améliorations de qualité**
- **Docstrings manquantes** → Ajouter des docstrings claires et complètes
- **Noms non descriptifs** → Renommer si vraiment nécessaire (avec prudence)
- **Code dupliqué** → Factoriser si c'est simple

### **4. LOW - Corrections de style**
- **Espacement PEP8** → Ajouter les espaces manquants
- **Lignes trop longues** → Découper si nécessaire
- **Noms de classes** → Corriger en PascalCase

---

## ✅ Ce que le Correcteur DOIT faire

1. ✅ **Corriger TOUS les problèmes** listés dans le rapport
2. ✅ **Conserver la logique originale** du code
3. ✅ **Respecter l'architecture** existante (noms de fonctions, classes, etc.)
4. ✅ **Ajouter des protections** contre les erreurs
5. ✅ **Respecter PEP8** dans le code corrigé
6. ✅ **Produire du code fonctionnel** qui peut s'exécuter sans erreur

---

## ❌ Ce que le Correcteur NE DOIT PAS faire

1. ❌ **Ne PAS réécrire complètement** le code
2. ❌ **Ne PAS changer la logique** métier
3. ❌ **Ne PAS renommer** les fonctions/classes (sauf si explicitement demandé)
4. ❌ **Ne PAS ajouter** de nouvelles fonctionnalités
5. ❌ **Ne PAS supprimer** de code fonctionnel
6. ❌ **Ne PAS ajouter** de texte explicatif avant/après le code
7. ❌ **Ne PAS utiliser** de balises markdown (pas de ```python)

---

## 📋 Règles de Correction par Type

### **Pour missing_import :**
```python
# Avant
def calculate():
    return math.sqrt(16)

# Après
import math

def calculate():
    return math.sqrt(16)
```

### **Pour missing_docstring :**
```python
# Avant
def add(a, b):
    return a + b

# Après
def add(a, b):
    """
    Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b
```

### **Pour division_by_zero :**
```python
# Avant
def average(numbers):
    return sum(numbers) / len(numbers)

# Après
def average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

### **Pour undefined_variable :**
```python
# Avant
def greet():
    print(message)

# Après
def greet(message="Hello"):
    print(message)
```

### **Pour pep8_spacing :**
```python
# Avant
def calculate(x,y):
    z=x+y
    return z

# Après
def calculate(x, y):
    z = x + y
    return z
```

---

## 🧪 Cas de Test

### **Exemple 1 : Correction simple**

**Entrée - Code buggé :**
```python
def hello():
    print(message)
```

**Entrée - Rapport :**
```json
{
  "issues": [
    {
      "line": 2,
      "type": "undefined_variable",
      "severity": "CRITICAL",
      "description": "Variable 'message' is not defined",
      "suggestion": "Define 'message' or pass as parameter"
    },
    {
      "line": 1,
      "type": "missing_docstring",
      "severity": "MEDIUM",
      "description": "Function has no docstring",
      "suggestion": "Add docstring"
    }
  ]
}
```

**Sortie attendue :**
```python
def hello(message="Hello"):
    """
    Print a message.
    
    Args:
        message (str): Message to print
    """
    print(message)
```

---

## 🎯 Critères de Succès

Le Correcteur est réussi si :
- ✅ Tous les bugs listés sont corrigés
- ✅ Le code produit est syntaxiquement valide
- ✅ Le code produit peut s'exécuter sans erreur
- ✅ La logique originale est préservée
- ✅ Pas de texte avant/après le code
- ✅ Format Python pur (pas de markdown)

---

## 🔄 Interface avec les Autres Agents

### **Depuis l'Agent Auditeur**
Le Correcteur reçoit le rapport JSON produit par l'Auditeur.

### **Vers l'Agent Testeur**
Le code corrigé sera testé par l'Agent Testeur. Si les tests échouent, le Correcteur peut être rappelé.

---

**Cette spécification sera utilisée pour :**
1. Rédiger le prompt système du Correcteur
2. Créer les fonctions Python de correction
3. Valider que les corrections sont correctes