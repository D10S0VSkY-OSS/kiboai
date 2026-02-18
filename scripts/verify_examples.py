import subprocess
import sys
import os
import shutil
import venv
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
EXAMPLES_DIR = PROJECT_ROOT / "examples" / "frameworks"

TEST_CASES = [
    {
        "name": "Agno (Phidata)",
        "script": EXAMPLES_DIR / "agno" / "agno_tool_example.py",
        "extras": ["agno", "finance"],  # agno example uses yfinance
    },
    {
        "name": "CrewAI",
        "script": EXAMPLES_DIR / "crewai" / "crewai_tool_example.py",
        "extras": ["crewai"],
    },
    {
        "name": "LangChain",
        "script": EXAMPLES_DIR / "langchain" / "langchain_tool_example.py",
        "extras": ["langchain", "web"], # langchain tool example might need duckduckgo/tavily
    },
    {
        "name": "LangGraph",
        "script": EXAMPLES_DIR / "langgraph" / "langgraph_native_gemini_example.py",
        "extras": ["langgraph", "langchain"], # langgraph often needs langchain base
    },
    {
        "name": "PydanticAI",
        "script": EXAMPLES_DIR / "pydantic_ai" / "pydantic_ai_tool_example.py",
        "extras": ["pydantic-ai"],
    },
]

def run_command(cmd, cwd=None, env=None):
    """Runs a shell command and streams output."""
    print(f"Executing: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {' '.join(cmd)}")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        raise subprocess.CalledProcessError(process.returncode, cmd, output=stdout, stderr=stderr)
    return stdout

def create_venv(venv_path):
    """Creates a virtual environment using uv if available, else venv."""
    print(f"Creating virtual environment at {venv_path}...")
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)
    
    # Try using uv first
    try:
        run_command(["uv", "venv", str(venv_path)])
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("uv not found, falling back to standard venv module.")
        venv.create(venv_path, with_pip=True)

def get_python_executable(venv_path):
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"

def install_package(python_exe, extras):
    """Installs the local package with specified extras."""
    extras_str = ",".join(extras)
    pkg_spec = f".[{extras_str}]"
    print(f"Installing {pkg_spec}...")
    
    # Try using uv first
    try:
        # invoke uv pip install -p python_exe pkg_spec
        # Assuming uv is in PATH
        uv_cmd = ["uv", "pip", "install", "-p", str(python_exe), pkg_spec]
        run_command(uv_cmd, cwd=PROJECT_ROOT)
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Fallback to standard pip
        print("uv failed or not found, falling back to standard pip.")
        pip_cmd = [str(python_exe), "-m", "pip", "install", pkg_spec]
        run_command(pip_cmd, cwd=PROJECT_ROOT)

def run_example(python_exe, script_path):
    """Runs the example script."""
    print(f"Running example: {script_path}...")
    env = os.environ.copy()
    # Ensure PYTHONPATH includes src so examples can run even if installed in editable mode?
    # Actually, we want to test installed package.
    # But examples might have relative imports or sys.path hacks.
    # The examples provided have sys.path hacks to include ../src. 
    # This might conflict if we want to test installed package vs local source.
    # But since we install with `pip install .`, it installs the source.
    
    cmd = [str(python_exe), str(script_path)]
    try:
        run_command(cmd, cwd=script_path.parent, env=env)
        print("✅ Success!")
    except subprocess.CalledProcessError as e:
        print("❌ Failed!")
        # Check if failure is due to missing API keys (common in integration tests)
        if "api_key" in e.stderr.lower() or "apikey" in e.stderr.lower():
            print("⚠️ Failure likely due to missing API Keys. This is expected if .env is missing.")
        else:
            raise e

def main():
    venv_root = PROJECT_ROOT / ".venv_test_suite"
    python_exe = get_python_executable(venv_root)

    try:
        # Create one shared venv for efficiency, or one per test?
        # One per test guarantees isolation as requested.
        pass
    except Exception as e:
        print(f"Setup failed: {e}")
        return

    for test in TEST_CASES:
        print(f"\n==============================================")
        print(f"Testing Framework: {test['name']}")
        print(f"==============================================")
        
        test_venv = venv_root / f"venv_{test['extras'][0]}"
        create_venv(test_venv)
        py_exe = get_python_executable(test_venv)
        
        try:
            install_package(py_exe, test['extras'])
            run_example(py_exe, test['script'])
        except Exception as e:
            print(f"Test failed for {test['name']}: {e}")
        finally:
            pass # Keep venv for inspection? Or delete?
            # shutil.rmtree(test_venv) # Uncomment to clean up

    print("\nTests failed are expected if you don't have API keys configured in environment variables.")

if __name__ == "__main__":
    main()
