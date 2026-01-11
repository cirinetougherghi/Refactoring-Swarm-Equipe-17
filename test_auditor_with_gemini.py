"""
Script de test manuel pour l'Agent Auditeur
Test avec Gemini 2.5 Flash sur les fichiers buggés
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from src.prompts.auditor_prompt import get_auditor_prompt

# Charge les variables d'environnement
load_dotenv()

# Configure l'API Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERREUR : Clé API non trouvée dans .env")
    exit(1)

genai.configure(api_key=api_key)


def test_auditor_on_file(file_path: str):
    """
    Teste l'Auditeur sur un fichier spécifique.
    
    Args:
        file_path (str): Chemin vers le fichier à analyser
    """
    print("=" * 80)
    print(f"🔍 TEST SUR : {file_path}")
    print("=" * 80)
    
    # 1. Lit le fichier
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {file_path}")
        return
    
    file_name = os.path.basename(file_path)
    print(f"📄 Fichier : {file_name}")
    print(f"📏 Lignes de code : {len(code_content.splitlines())}")
    
    # 2. Génère le prompt avec la fonction helper
    print("\n⚙️  Génération du prompt...")
    prompt = get_auditor_prompt(file_name, code_content)
    print(f"✅ Prompt généré ({len(prompt)} caractères, ~{len(prompt)//4} tokens)")
    
    # 3. Envoie à Gemini
    print("\n🤖 Envoi à Gemini 2.5 Flash...")
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        raw_response = response.text
        
        print(f"✅ Réponse reçue ({len(raw_response)} caractères)")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'appel API : {e}")
        return
    
    # 4. Affiche la réponse brute
    print("\n" + "=" * 80)
    print("📨 RÉPONSE BRUTE DE GEMINI :")
    print("=" * 80)
    print(raw_response)
    print("=" * 80)
    
    # 5. Tente de parser le JSON
    print("\n🔍 ANALYSE DE LA RÉPONSE :")
    
    # Nettoie la réponse (enlève les balises markdown si présentes)
    cleaned_response = raw_response.strip()
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]  # Enlève ```json
    if cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]  # Enlève ```
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]  # Enlève ```
    cleaned_response = cleaned_response.strip()
    
    # Tente de parser le JSON
    try:
        result = json.loads(cleaned_response)
        print("✅ JSON VALIDE !")
        
        # Affiche les résultats
        print(f"\n📊 RÉSULTATS :")
        print(f"   Fichier analysé : {result.get('file', 'N/A')}")
        print(f"   Total de problèmes : {result.get('total_issues', 0)}")
        
        issues = result.get('issues', [])
        if issues:
            print(f"\n🐛 BUGS DÉTECTÉS ({len(issues)}) :")
            for i, issue in enumerate(issues, 1):
                print(f"\n   [{i}] Ligne {issue.get('line', '?')}")
                print(f"       Type : {issue.get('type', 'N/A')}")
                print(f"       Sévérité : {issue.get('severity', 'N/A')}")
                print(f"       Description : {issue.get('description', 'N/A')}")
                print(f"       Suggestion : {issue.get('suggestion', 'N/A')}")
        else:
            print("\n✨ Aucun problème détecté - Code propre !")
        
        # Sauvegarde le résultat
        output_file = f"test_results_{file_name.replace('.py', '')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Résultat sauvegardé dans : {output_file}")
        
    except json.JSONDecodeError as e:
        print(f"❌ ERREUR : JSON INVALIDE !")
        print(f"   Erreur : {e}")
        print(f"\n⚠️  PROBLÈME : Gemini a ajouté du texte avant/après le JSON")
        print(f"   ou le JSON est mal formé.")
        
        # Sauvegarde la réponse brute pour analyse
        error_file = f"test_error_{file_name.replace('.py', '')}.txt"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(raw_response)
        print(f"\n💾 Réponse brute sauvegardée dans : {error_file}")
    
    print("\n" + "=" * 80)


def main():
    """Fonction principale - teste plusieurs fichiers"""
    
    print("\n" + "🧪" * 40)
    print("TEST DE L'AGENT AUDITEUR AVEC GEMINI 2.5 FLASH")
    print("🧪" * 40 + "\n")
    
    # Liste des fichiers à tester
    test_files = [
         "sandbox/test_samples/buggy_code_simple.py",  
         "sandbox/test_samples/buggy_code_medium.py", 
         "sandbox/test_samples/buggy_code_complex.py",
         "sandbox/test_samples/buggy_code_edge_cases.py",
    ]
    
    for file_path in test_files:
        test_auditor_on_file(file_path)
        print("\n")
    
    print("✅ TESTS TERMINÉS !\n")

if __name__ == "__main__":
    main()