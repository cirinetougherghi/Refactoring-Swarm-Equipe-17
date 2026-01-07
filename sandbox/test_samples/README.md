---

### . `buggy_code_complex.py`
**Niveau de difficulté :** Difficile  
**Nombre de bugs :** 15  
**Bugs présents :**
- ❌ CRITICAL : Import manquant (math)
- ❌ HIGH : Multiples divisions par zéro
- ❌ HIGH : Accès à dictionnaires/listes avec valeurs None
- ❌ HIGH : Fichier inexistant
- ❌ MEDIUM : 7 docstrings manquantes
- ❌ LOW : 4 violations PEP8

**Objectif :** Test de robustesse sur code complexe avec nombreux bugs

---

### . `buggy_code_edge_cases.py`
**Niveau de difficulté :** Expert  
**Nombre de bugs :** 14 (tous HIGH/CRITICAL)  
**Bugs présents :**
- ❌ HIGH : 10 erreurs sur cas limites (listes vides, None, division par zéro)
- ❌ MEDIUM : 5 docstrings manquantes

**Objectif :** Test des cas limites et erreurs subtiles