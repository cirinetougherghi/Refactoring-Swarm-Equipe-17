import os
import subprocess

TEST_DIR = "sandbox/test_dataset"

def validate_test_files():
    files = [f for f in os.listdir(TEST_DIR) if f.endswith('.py')]
    
    print(f"🔍 Validation de {len(files)} fichiers de test...")
    
    for file in files:
        filepath = os.path.join(TEST_DIR, file)
        print(f"\n📄 {file}")
        
        # Test Pylint
        result = subprocess.run(
            ["pylint", filepath],
            capture_output=True,
            text=True
        )
        score_line = [l for l in result.stdout.split('\n') if 'rated at' in l]
        if score_line:
            print(f"  📊 Score Pylint : {score_line[0]}")
        
        # Test syntaxe
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                compile(f.read(), filepath, 'exec')
            print("  ✅ Syntaxe valide")
        except SyntaxError as e:
            print(f"  ❌ Erreur syntaxe : {e}")

if __name__ == "__main__":
    validate_test_files()