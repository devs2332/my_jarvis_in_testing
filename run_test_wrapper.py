import subprocess
import sys
import os

# Add project root to PYTHONPATH for the subprocess2/20/2026
env = os.environ.copy()
env["PYTHONPATH"] = os.getcwd()

res = subprocess.run([sys.executable, 'tests/test_feature_toggles.py'], capture_output=True, text=True, env=env)
print("STDOUT:\n", res.stdout)
print("STDERR:\n", res.stderr)
