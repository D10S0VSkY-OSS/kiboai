import subprocess
import sys
import os
import shutil
import venv
from pathlib import Path
import re

# Load .env file
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
EXAMPLES_DIR = PROJECT_ROOT / "examples" / "frameworks"

# TestPyPI Configuration
TEST_PYPI_INDEX = "https://test.pypi.org/simple/"
PYPI_INDEX = "https://pypi.org/simple/"

TEST_CASES = [
    {
        "name": "Agno (Phidata)",
        "script": EXAMPLES_DIR / "agno" / "agno_tool_example.py",
        "extras": ["agno", "finance"],
    },
    {
        "name": "CrewAI",
        "script": EXAMPLES_DIR / "crewai" / "crewai_tool_example.py",
        "extras": ["crewai"],
    },
    {
        "name": "LangChain",
        "script": EXAMPLES_DIR / "langchain" / "langchain_tool_example.py",
        "extras": ["langchain", "web"],
    },
    {
        "name": "LangGraph",
        "script": EXAMPLES_DIR / "langgraph" / "langgraph_native_gemini_example.py",
        "extras": ["langgraph", "langchain"],
    },
    {
        "name": "PydanticAI",
        "script": EXAMPLES_DIR / "pydantic_ai" / "pydantic_ai_tool_example.py",
        "extras": ["pydantic-ai"],
    },
]


def get_package_version():
    """Extracts package version from pyproject.toml."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    with open(pyproject_path, "r") as f:
        content = f.read()
        match = re.search(r'version = "(.*?)"', content)
        if match:
            return match.group(1)
    return None


def run_command(cmd, cwd=None, env=None):
    """Runs a shell command and streams output."""
    print(f"Executing: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd, cwd=cwd, env=env, stdout=sys.stdout, stderr=sys.stderr, text=True
    )
    process.wait()
    if process.returncode != 0:
        print(f"Error executing command: {' '.join(cmd)}")
        raise subprocess.CalledProcessError(process.returncode, cmd)
    return "Output streamed directly to console"


def create_venv(venv_path):
    """Creates a virtual environment using uv."""
    print(f"Creating virtual environment at {venv_path}...")
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)

    try:
        run_command(["uv", "venv", str(venv_path)])
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("uv not found, falling back to standard venv module.")
        venv.create(venv_path, with_pip=True)


def get_python_executable(venv_path):
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def install_from_testpypi(python_exe, version, extras):
    """Installs the package from TestPyPI with specified extras."""
    extras_str = ",".join(extras)
    pkg_spec = f"kiboai[{extras_str}]=={version}"
    print(f"Installing {pkg_spec} from TestPyPI...")

    # Construct uv pip install command
    # uv pip install -p <python> --index-url <testpypi> --extra-index-url <pypi> package
    uv_cmd = [
        "uv",
        "pip",
        "install",
        "-p",
        str(python_exe),
        "--index-url",
        TEST_PYPI_INDEX,
        "--extra-index-url",
        PYPI_INDEX,
        pkg_spec,
    ]

    try:
        run_command(uv_cmd, cwd=PROJECT_ROOT)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("uv failed or not found, falling back to standard pip.")
        # Only standard pip fallback (might be slower and tricky with index-url mixing)
        pip_cmd = [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--index-url",
            TEST_PYPI_INDEX,
            "--extra-index-url",
            PYPI_INDEX,
            pkg_spec,
        ]
        run_command(pip_cmd, cwd=PROJECT_ROOT)


def run_example(python_exe, script_path):
    """Runs the example script."""
    print(f"Running example: {script_path}...")
    env = os.environ.copy()

    # We want to ensure we use the INSTALLED package, not the local source.
    # The examples usually append 'src' to sys.path.
    # Since sys.path.append adds to the END, and site-packages is earlier,
    # the installed package *should* take precedence.
    # To be absolutely sure, we can set PYTHONPATH to exclude src if it was explicitly set?
    # No, let's trust sys.path order.

    cmd = [str(python_exe), str(script_path)]
    try:
        run_command(cmd, cwd=script_path.parent, env=env)
        print("✅ Success!")
    except subprocess.CalledProcessError as e:
        print("❌ Failed!")
        # Check if failure is due to missing API keys
        if "api_key" in e.stderr.lower() or "apikey" in e.stderr.lower():
            print(
                "⚠️ Failure likely due to missing API Keys. This is expected if .env is missing."
            )
        else:
            # It might fail if package not found or import error
            raise e


def main():
    version = get_package_version()
    if not version:
        print("❌ Could not determine package version from pyproject.toml")
        return

    print(f"🔍 Detected version: {version}")
    print(f"🌍 Using Index: {TEST_PYPI_INDEX} (with fallback to {PYPI_INDEX})")

    venv_root = PROJECT_ROOT / ".venv_test_pypi_suite"

    for test in TEST_CASES:
        print(f"\n==============================================")
        print(f"Testing Install & Run for: {test['name']}")
        print(f"==============================================")

        test_venv = venv_root / f"venv_{test['extras'][0]}"
        create_venv(test_venv)
        py_exe = get_python_executable(test_venv)

        try:
            install_from_testpypi(py_exe, version, test["extras"])

            # Verify installation location
            verify_cmd = [str(py_exe), "-c", "import kiboai; print(kiboai.__file__)"]
            output = run_command(verify_cmd)
            print(f"✅ Verified installed locations: {output.strip()}")
            if "site-packages" not in output and "dist-packages" not in output:
                print(
                    "⚠️ WARMING: It seems to be importing from source/local path, not installed package!"
                )

            run_example(py_exe, test["script"])
        except Exception as e:
            print(f"❌ Test failed for {test['name']}: {e}")

    print("\nTests completed.")


if __name__ == "__main__":
    main()
