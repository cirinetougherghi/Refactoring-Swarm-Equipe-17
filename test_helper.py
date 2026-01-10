"""Test de la fonction helper"""

from src.prompts.auditor_prompt import get_auditor_prompt

# Code de test simple
test_code = """
def hello():
    print(message)
"""

# Utilise la fonction helper
prompt = get_auditor_prompt("test.py", test_code)

print("✅ Fonction helper fonctionne !")
print(f"📏 Longueur du prompt : {len(prompt)} caractères")
print(f"🎯 Contient 'RÈGLES ABSOLUES' : {'RÈGLES ABSOLUES' in prompt}")
print(f"🎯 Contient le code : {test_code.strip() in prompt}")
