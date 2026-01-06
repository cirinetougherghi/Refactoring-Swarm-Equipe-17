"""
Test de connexion à Gemini
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Charge les variables d'environnement
load_dotenv()

# Configure l'API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERREUR : Clé API non trouvée dans .env")
    exit(1)

genai.configure(api_key=api_key)

# Teste avec un prompt simple
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content("Dis bonjour en une phrase")

print("✅ Connexion réussie !")
print(f"Réponse de Gemini : {response.text}")
