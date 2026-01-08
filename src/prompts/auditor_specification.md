# 🔍 Spécification de l'Agent Auditeur

**Créé par :** Ingénieur Prompt  
**Date :** 08/01/2026  
**Version :** 1.0

---

## 🎯 Mission Principale

L'Agent Auditeur est le **premier agent** du système Refactoring Swarm.

**Sa mission :**
> Analyser du code Python pour détecter TOUS les problèmes (bugs, erreurs, mauvaises pratiques) et produire un rapport JSON structuré que l'Agent Correcteur pourra utiliser.

---

## 📥 Entrées

L'Auditeur reçoit :
1. **Nom du fichier** (exemple : `buggy_code.py`)
2. **Contenu du code** (texte brut Python)

---

## 📤 Sortie

L'Auditeur produit un **objet JSON** avec cette structure exacte :
```json
{
  "file": "nom_du_fichier.py",
  "total_issues": 5,
  "issues": [
    {
      "line": 10,
      "type": "syntax_error",
      "severity": "HIGH",
      "description": "Variable 'message' is not defined",
      "suggestion": "Define the variable 'message' before using it, or pass it as a parameter"
    },
    {
      "line": 15,
      "type": "missing_docstring",
      "severity": "MEDIUM",
      "description": "Function 'calculate_sum' has no docstring",
      "suggestion": "Add a docstring describing the function's purpose, parameters, and return value"
    }
  ]
}
```

---

## 🐛 Types de Problèmes à Détecter

### 1. **Erreurs de Syntaxe** (CRITICAL/HIGH)
- Variables non définies
- Imports manquants
- Utilisation incorrecte de modules (ex: `cos()` au lieu de `math.cos()`)
- Noms de classes/fonctions invalides

### 2. **Erreurs de Logique** (CRITICAL/HIGH)
- Division par zéro
- Index hors limites
- Accès à des éléments de listes/dicts vides
- Opérations sur `None`
- Fichiers inexistants
- Clés de dictionnaires inexistantes

### 3. **Problèmes de Qualité** (MEDIUM)
- Fonctions sans docstrings
- Classes sans docstrings
- Méthodes sans docstrings
- Pas de type hints
- Nommage non conforme (variables, fonctions, classes)

### 4. **Violations PEP8** (LOW)
- Pas d'espaces autour des opérateurs (`x=5` au lieu de `x = 5`)
- Pas d'espaces après les virgules (`def f(a,b)` au lieu de `def f(a, b)`)
- Lignes trop longues (>79 caractères)
- Imports mal organisés

---

## 📊 Niveaux de Sévérité

| Niveau | Quand l'utiliser | Exemples |
|--------|------------------|----------|
| **CRITICAL** | Le code NE PEUT PAS s'exécuter | Import manquant, erreur de syntaxe majeure |
| **HIGH** | Le code plante à l'exécution | Division par zéro, index hors limites, accès à None |
| **MEDIUM** | Mauvaise qualité mais fonctionne | Docstrings manquantes, pas de type hints |
| **LOW** | Violations de style | PEP8, espaces, formatage |

---

## ✅ Ce que l'Auditeur DOIT faire

1. ✅ **Analyser ligne par ligne** le code fourni
2. ✅ **Détecter TOUS les problèmes** réels
3. ✅ **Produire UNIQUEMENT du JSON** (pas de texte avant/après)
4. ✅ **Indiquer le numéro de ligne exact** de chaque problème
5. ✅ **Classifier correctement** la sévérité
6. ✅ **Donner une suggestion** de correction pour chaque problème

---

## ❌ Ce que l'Auditeur NE DOIT PAS faire

1. ❌ **Ne JAMAIS inventer** de bugs qui n'existent pas
2. ❌ **Ne JAMAIS ajouter** de texte avant ou après le JSON
3. ❌ **Ne JAMAIS corriger** le code (c'est le rôle du Correcteur)
4. ❌ **Ne JAMAIS ignorer** un bug détecté
5. ❌ **Ne JAMAIS** utiliser des sévérités incorrectes

---

## 🧪 Cas de Test

### Cas 1 : Code propre (0 bugs)
**Entrée :** `clean_code.py` (avec docstrings, type hints, PEP8)  
**Sortie attendue :**
```json
{
  "file": "clean_code.py",
  "total_issues": 0,
  "issues": []
}
```

### Cas 2 : Code avec 1 bug simple
**Entrée :**
```python
def hello():
    print(message)
```

**Sortie attendue :**
```json
{
  "file": "test.py",
  "total_issues": 2,
  "issues": [
    {
      "line": 2,
      "type": "undefined_variable",
      "severity": "HIGH",
      "description": "Variable 'message' is not defined",
      "suggestion": "Define 'message' before using it"
    },
    {
      "line": 1,
      "type": "missing_docstring",
      "severity": "MEDIUM",
      "description": "Function 'hello' has no docstring",
      "suggestion": "Add a docstring"
    }
  ]
}
```

---

## 🎯 Critères de Succès

L'Auditeur est réussi si :
- ✅ Taux de détection > 90% sur nos fichiers de test
- ✅ Taux de faux positifs < 5%
- ✅ JSON toujours valide
- ✅ Temps d'analyse < 30 secondes par fichier

---

## 🔄 Interfaces avec les Autres Agents

### Vers l'Agent Correcteur
L'Auditeur produit le JSON que le Correcteur utilisera pour savoir quoi corriger.

### Vers l'Agent Testeur
Après correction, le Testeur pourra re-lancer l'Auditeur pour vérifier qu'il ne reste plus de bugs.

---

**Cette spécification sera utilisée pour :**
1. Rédiger le prompt système
2. Créer les fonctions Python
3. Valider que le système fonctionne