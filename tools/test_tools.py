import subprocess
import json
import os

def run_pytest(target_dir="sandbox"):
    """
    Exécute pytest sur un répertoire donné et retourne les résultats au format JSON
    """
    # Vérifie si le répertoire existe
    if not os.path.exists(target_dir):
        raise FileNotFoundError(f"Le répertoire {target_dir} n'existe pas")

    # Lance pytest avec génération du rapport JSON
    result = subprocess.run(
        ["pytest", target_dir, "--json-report", "--json-report-file=report.json"],
        capture_output=True,
        text=True
    )

    # Lit le rapport
    if os.path.exists("report.json"):
        with open("report.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"error": "Le rapport JSON n'a pas été créé", "stdout": result.stdout, "stderr": result.stderr}

    # Affiche le rapport pour débogage
    print("=== Rapport pytest ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    return data
