# coding: utf-8
import os
import sys
from pathlib import Path

print("="*80)
print("TEST RAPIDE")
print("="*80)

current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

print("\nDossier:", project_root)

# 1. Dependances
print("\n1. Verification dependances...")

try:
    import google.generativeai as genai
    print("   OK google-generativeai")
except ImportError:
    print("   ERREUR google-generativeai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("   OK python-dotenv")
except ImportError:
    print("   ERREUR python-dotenv")
    sys.exit(1)

# 2. Cle API
print("\n2. Verification cle API...")
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("   ERREUR: Cle API manquante")
    sys.exit(1)
else:
    print("   OK Cle API trouvee")
    genai.configure(api_key=api_key)

# 3. Imports agents
print("\n3. Verification imports agents...")

try:
    from src.agents.auditor_agent import AuditorAgent
    print("   OK AuditorAgent")
except Exception as e:
    print("   ERREUR AuditorAgent:", e)
    sys.exit(1)

try:
    from src.agents.fixer_agent import FixerAgent
    print("   OK FixerAgent")
except Exception as e:
    print("   ERREUR FixerAgent:", e)
    sys.exit(1)

try:
    from src.agents.judge_agent import JudgeAgent
    print("   OK JudgeAgent")
except Exception as e:
    print("   ERREUR JudgeAgent:", e)
    sys.exit(1)

try:
    from src.orchestrator import Orchestrator
    print("   OK Orchestrator")
except Exception as e:
    print("   ERREUR Orchestrator:", e)
    sys.exit(1)

print("\n" + "="*80)
print("TOUS LES TESTS PASSES!")
print("="*80)
print("\nProchaine etape:")
print("python -m tests.test_integration_complete")

sys.exit(0)