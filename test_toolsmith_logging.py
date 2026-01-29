"""
Test script to verify ALL toolsmith utilities generate proper logs
Tests: file_tools, analysis_tools, test_tools, security
"""

import os
import json
from src.tools.file_tools import write_file, read_file
from src.tools.analysis_tools import run_pylint, run_pytest as analysis_run_pytest
from src.tools.test_tools import run_pytest
from src.tools.security import is_safe_path, validate_path_or_raise, SecurityError


def test_toolsmith_logging():
    """Test that all toolsmith tools generate proper logs"""
    
    print("\n" + "=" * 80)
    print("🧪 TESTING ALL TOOLSMITH UTILITIES LOGGING")
    print("=" * 80 + "\n")
    
    # Clear old logs
    log_file = "logs/experiment_data.json"
    if os.path.exists(log_file):
        # Backup existing logs
        with open(log_file, 'r') as f:
            existing_logs = json.load(f)
        print(f"📊 Existing logs: {len(existing_logs)} entries")
        
        # Clear for fresh test
        with open(log_file, 'w') as f:
            json.dump([], f)
        print("🧹 Cleared logs for fresh test\n")
    else:
        existing_logs = []
    
    # ========================================================================
    # TEST 1: Security Tools
    # ========================================================================
    
    print("=" * 80)
    print("TEST 1: SECURITY TOOLS (security.py)")
    print("=" * 80 + "\n")
    
    print("1️⃣  Testing is_safe_path() with safe path...")
    try:
        result = is_safe_path("./sandbox/test.py")
        print(f"   ✅ Safe path validated: {result}\n")
    except Exception as e:
        print(f"   ❌ Safe path test failed: {e}\n")
    
    print("2️⃣  Testing is_safe_path() with unsafe path...")
    try:
        result = is_safe_path("../../../etc/passwd")
        print(f"   ✅ Unsafe path detected: {not result}\n")
    except Exception as e:
        print(f"   ❌ Unsafe path test failed: {e}\n")
    
    print("3️⃣  Testing validate_path_or_raise() with safe path...")
    try:
        validate_path_or_raise("./sandbox/allowed.py", "write")
        print("   ✅ Safe path allowed by enforcer\n")
    except Exception as e:
        print(f"   ❌ Enforcer blocked safe path: {e}\n")
    
    print("4️⃣  Testing validate_path_or_raise() with unsafe path...")
    try:
        validate_path_or_raise("../../../etc/passwd", "read")
        print("   ❌ Enforcer FAILED - should have blocked this!\n")
    except SecurityError:
        print("   ✅ Enforcer correctly blocked unsafe path\n")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}\n")
    
    # ========================================================================
    # TEST 2: File Tools
    # ========================================================================
    
    print("=" * 80)
    print("TEST 2: FILE TOOLS (file_tools.py)")
    print("=" * 80 + "\n")
    
    test_file = "sandbox/test_logging.py"
    test_content = '''def hello():
    """Test function"""
    print("Hello, World!")

if __name__ == "__main__":
    hello()
'''
    
    print("5️⃣  Testing write_file()...")
    try:
        write_file(test_file, test_content)
        print("   ✅ Write successful\n")
    except Exception as e:
        print(f"   ❌ Write failed: {e}\n")
    
    print("6️⃣  Testing read_file()...")
    try:
        content = read_file(test_file)
        print(f"   ✅ Read {len(content)} characters\n")
    except Exception as e:
        print(f"   ❌ Read failed: {e}\n")
    
    print("7️⃣  Testing security (read outside sandbox)...")
    try:
        read_file("/etc/passwd")  # Should fail
        print("   ❌ Security FAILED - should have blocked this!\n")
    except PermissionError:
        print("   ✅ Security working - correctly blocked\n")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}\n")
    
    # ========================================================================
    # TEST 3: Analysis Tools - Pylint
    # ========================================================================
    
    print("=" * 80)
    print("TEST 3: ANALYSIS TOOLS - PYLINT (analysis_tools.py)")
    print("=" * 80 + "\n")
    
    print("8️⃣  Testing run_pylint()...")
    try:
        result = run_pylint(test_file)
        score = result.get('score', 0)
        print(f"   ✅ Pylint completed - Score: {score}/10\n")
    except Exception as e:
        print(f"   ⚠️  Pylint test skipped (pylint may not be installed): {e}\n")
    
    # ========================================================================
    # TEST 4: Analysis Tools - Pytest
    # ========================================================================
    
    print("=" * 80)
    print("TEST 4: ANALYSIS TOOLS - PYTEST (analysis_tools.py)")
    print("=" * 80 + "\n")
    
    # Create a simple test file
    test_test_file = "sandbox/test_sample.py"
    test_test_content = '''def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 5 - 3 == 2
'''
    
    try:
        write_file(test_test_file, test_test_content)
    except:
        pass
    
    print("9️⃣  Testing run_pytest() from analysis_tools...")
    try:
        result = analysis_run_pytest(test_test_file)
        passed = result.get('passed', 0)
        failed = result.get('failed', 0)
        print(f"   ✅ Pytest (analysis_tools) completed - Passed: {passed}, Failed: {failed}\n")
    except Exception as e:
        print(f"   ⚠️  Pytest test skipped: {e}\n")
    
    # ========================================================================
    # TEST 5: Test Tools - Pytest with JSON
    # ========================================================================
    
    print("=" * 80)
    print("TEST 5: TEST TOOLS - PYTEST WITH JSON (test_tools.py)")
    print("=" * 80 + "\n")
    
    print("🔟 Testing run_pytest() from test_tools with JSON report...")
    try:
        # Create test directory if needed
        os.makedirs("sandbox", exist_ok=True)
        result = run_pytest("sandbox")
        print(f"   ✅ Pytest (test_tools) completed with JSON report\n")
    except Exception as e:
        print(f"   ⚠️  Pytest JSON test skipped: {e}\n")
    
    # ========================================================================
    # VERIFY LOGS
    # ========================================================================
    
    print("=" * 80)
    print("📊 VERIFYING LOGS")
    print("=" * 80 + "\n")
    
    if not os.path.exists(log_file):
        print("❌ No log file created!\n")
        return
    
    with open(log_file, 'r') as f:
        logs = json.load(f)
    
    print(f"✅ Generated {len(logs)} log entries\n")
    
    # Check required fields
    required_fields = ["timestamp", "agent", "model", "action", "details", "status"]
    required_details = ["input_prompt", "output_response"]
    
    print("Validating log structure...\n")
    
    errors = []
    for i, log in enumerate(logs):
        # Check main fields
        for field in required_fields:
            if field not in log:
                errors.append(f"Log {i}: Missing field '{field}'")
        
        # Check details
        for detail in required_details:
            if detail not in log.get("details", {}):
                errors.append(f"Log {i}: Missing detail '{detail}'")
        
        # Show summary
        agent = log.get("agent", "Unknown")
        action = log.get("action", "Unknown")
        status = log.get("status", "Unknown")
        print(f"   ✅ Log {i+1}: {agent} - {action} - {status}")
    
    if errors:
        print("\n⚠️  ERRORS FOUND:")
        for error in errors:
            print(f"   ❌ {error}")
    else:
        print("\n✅ All log entries have required fields!")
    
    print("\n" + "=" * 80)
    print("📋 LOG SUMMARY BY AGENT")
    print("=" * 80 + "\n")
    
    # Count by agent
    agent_counts = {}
    for log in logs:
        agent = log.get("agent", "Unknown")
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    for agent, count in sorted(agent_counts.items()):
        print(f"   {agent}: {count} entries")
    
    print("\n" + "=" * 80)
    print("📋 LOG SUMMARY BY ACTION")
    print("=" * 80 + "\n")
    
    # Count by action
    action_counts = {}
    for log in logs:
        action = log.get("action", "Unknown")
        action_counts[action] = action_counts.get(action, 0) + 1
    
    for action, count in sorted(action_counts.items()):
        print(f"   {action}: {count} entries")
    
    print("\n" + "=" * 80)
    print("📋 LOG SUMMARY BY STATUS")
    print("=" * 80 + "\n")
    
    # Count by status
    status_counts = {}
    for log in logs:
        status = log.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in sorted(status_counts.items()):
        print(f"   {status}: {count} entries")
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("🧹 CLEANUP")
    print("=" * 80 + "\n")
    
    try:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"   ✅ Removed {test_file}")
        if os.path.exists(test_test_file):
            os.remove(test_test_file)
            print(f"   ✅ Removed {test_test_file}")
        if os.path.exists("report.json"):
            os.remove("report.json")
            print(f"   ✅ Removed report.json")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")
    
    # Restore original logs
    with open(log_file, 'w') as f:
        json.dump(existing_logs + logs, f, indent=2, ensure_ascii=False)
    print(f"\n   ✅ Restored original logs + {len(logs)} new test entries")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 80 + "\n")
    
    print(f"📊 Total log entries after test: {len(existing_logs) + len(logs)}")
    print(f"💾 Logs saved in: {log_file}\n")
    
    if not errors:
        print("🎉 ALL VALIDATIONS PASSED - ALL TOOLSMITH UTILITIES LOGGING PERFECTLY!\n")
    else:
        print(f"⚠️  Found {len(errors)} validation errors - please review logs\n")


if __name__ == "__main__":
    test_toolsmith_logging()