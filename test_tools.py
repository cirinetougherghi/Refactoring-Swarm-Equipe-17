import os
import subprocess
import json
import shutil

SANDBOX_DIR = "sandbox"


def run_pylint(file_path):
    result = subprocess.run(["pylint", file_path, "-f", "json"], capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        score = data[0]["score"] if data else 0
    except Exception:
        score = 0
    return score


def run_pytest(target):
    result = subprocess.run(["pytest", target, "--disable-warnings", "-q", "--tb=short"], capture_output=True, text=True)
    passed = result.stdout.count("PASSED")
    failed = result.stdout.count("FAILED")
    return {"passed": passed, "failed": failed}


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_tools():
    report = {"files": {}, "summary": {"total_files": 0, "total_passed": 0, "total_failed": 0}}
    for f in os.listdir(SANDBOX_DIR):
        if f.endswith(".py"):
            path = os.path.join(SANDBOX_DIR, f)
            
            # pylint
            score = run_pylint(path)
            
            # read_file / write_file
            content = read_file(path)
            copy_path = os.path.join(SANDBOX_DIR, f"{f}_copy.py")
            write_file(copy_path, content)
            
            # pytest
            test_res = run_pytest(path)
            
        
            report["files"][f] = {"pylint_score": score, **test_res}
            report["summary"]["total_files"] += 1
            report["summary"]["total_passed"] += test_res["passed"]
            report["summary"]["total_failed"] += test_res["failed"]
    
# report.json
    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    
    print("report json creé")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    test_tools()
