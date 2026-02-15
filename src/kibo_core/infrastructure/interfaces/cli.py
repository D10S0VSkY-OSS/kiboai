import sys
import subprocess
import shutil
import argparse
import os


def _check_executable(name: str) -> str:
    """Checks if an executable exists in PATH."""
    exe = shutil.which(name)
    if not exe:
        print(f"Error: '{name}' executable not found. Please install dependencies.")
        sys.exit(1)
    return exe


def handle_memory(args):
    try:
        from kibo_core.infrastructure.memory import KiboMemory

        mem = KiboMemory()

        if args.mem_action == "add":
            text = " ".join(args.text)
            mem.add(text, user_id="cli_user")
            print(f"✅ Added memory: {text}")

        elif args.mem_action == "search":
            query = " ".join(args.query)
            results = mem.search(query, user_id="cli_user")
            print(f"🔍 Found {len(results)} memories:")
            for r in results:
                content = r.get("memory", r) if isinstance(r, dict) else r
                print(f"- {content}")

        elif args.mem_action == "list":
            results = mem.get_all(user_id="cli_user")
            print(f"📂 All memories for cli_user:")
            for r in results:
                content = r.get("memory", r) if isinstance(r, dict) else r
                print(f"- {content}")
        else:
            print("Usage: kibo memory [add | search | list]")

    except ImportError:
        print("❌ Error: mem0ai not installed/configured properly.")
    except Exception as e:
        from traceback import print_exc

        print(f"❌ Error accessing memory: {e}")


def handle_serve(args):
    try:
        from kibo_core.infrastructure.server.app import start_agent_server

        start_agent_server(args.file, args.host, args.port, args.name)
    except ImportError:
        print(
            "❌ Error: 'kibo serve' requires 'fastapi' and 'uvicorn'. Please install them."
        )
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


def handle_start(args, unknown_args):

    if args.service == "db":
        print("🚀 Starting ChromaDB Server...")
        chroma_cmd = ["chroma", "run", "--port", "8000", "--path", "chroma_db"]
        try:
            subprocess.run(chroma_cmd, check=True)
        except KeyboardInterrupt:
            print("\n🛑 ChromaDB stopped.")
        except Exception as e:
            print(f"❌ Error starting ChromaDB: {e}")
        return

    ray_exe = _check_executable("ray")
    print("🚀 Starting Kibo Node...")

    start_flags = ["--disable-usage-stats"]

    is_head = "--head" in unknown_args

    if is_head:
        start_flags.append("--include-dashboard=false")
        print("Initializing Kibo Cluster Coordinator (Head Node)...")
    else:
        print("Initializing Kibo Worker Node...")

    final_args = unknown_args + [f for f in start_flags if f not in unknown_args]

    cmd = [ray_exe, "start"] + final_args

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        for line in result.stdout.split("\n"):
            if "Local node IP" in line:
                print(f"  {line.strip()}")

        print("✅ Kibo Node started successfully.")

        port = "6379"
        for i, arg in enumerate(final_args):
            if arg.startswith("--port="):
                port = arg.split("=")[1]
            elif arg == "--port" and i + 1 < len(final_args):
                port = final_args[i + 1]

        print("\nNext steps:")
        if is_head:
            print(f"  To join a worker node to this cluster:")
            print(f"    kibo start --address='<THIS_IP>:{port}'")
        else:
            print(f"  To check cluster status:")
            print(f"    kibo status")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Kibo Node.")
        print(f"\n{e.stderr}")
        print("\nTroubleshooting tips:")
        print("1. If 'Address already in use', try 'kibo stop' or 'pkill -f ray'")
        print("2. Or use a different port: 'kibo start --head --port=6380'")
        sys.exit(e.returncode)


def handle_start_all(args):
    print("🚀 Launching Kibo AI Platform (Gateway + Head Node)...")

    kibo_cmd = [sys.executable, "-m", "kibo_core.infrastructure.interfaces.cli"]

    print("\n[1/2] Starting Gateway...")
    proxy_cmd = kibo_cmd + ["proxy", "start", "-d"]
    if os.path.exists("examples/proxy_config.yaml"):
        proxy_cmd.extend(["--config", "examples/proxy_config.yaml"])

    try:
        subprocess.run(proxy_cmd, check=True)
        print("✅ Gateway started.")
    except subprocess.CalledProcessError:
        print("❌ Failed to start Gateway.")
        sys.exit(1)

    print("\n[2/2] Starting Cluster Head Node...")
    node_cmd = kibo_cmd + ["start", "--head", "--port=6379"]

    try:
        subprocess.run(node_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ Failed to start Head Node. Stopping Gateway...")
        try:
            import signal
            import psutil
            import time

            if os.path.exists("gateway.pid"):
                with open("gateway.pid", "r") as pid_file:
                    content = pid_file.read().strip()

                if content:
                    pid = int(content)
                    try:
                        proc = psutil.Process(pid)
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        print("✅ Gateway stopped.")
                    except (psutil.NoSuchProcess, ProcessLookupError):
                        pass
                    except (psutil.AccessDenied, PermissionError):
                        print("❌ Permission denied when stopping gateway.")

                try:
                    os.remove("gateway.pid")
                except OSError:
                    pass

        except Exception as cleanup_error:
            print(f"⚠️ Error cleaning up gateway: {cleanup_error}")

        sys.exit(e.returncode)


def handle_stop(args, unknown_args):
    ray_exe = _check_executable("ray")
    print("🛑 Stopping Kibo Node...")
    cmd = [ray_exe, "stop"] + unknown_args
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Kibo Node stopped.")
    else:
        print("❌ Failed to stop Kibo Node.")
        if result.stderr:
            print(f"Error details:\n{result.stderr}")


def handle_status(args, unknown_args):
    ray_exe = _check_executable("ray")
    cmd = [ray_exe, "status"] + unknown_args
    subprocess.run(cmd)


def handle_proxy(args, unknown_args):
    litellm_exe = shutil.which("litellm")
    if not litellm_exe:
        litellm_exe_cmd = [sys.executable, "-m", "litellm"]
    else:
        litellm_exe_cmd = [litellm_exe]

    if args.proxy_action == "start":
        print("🚀 Starting Kibo Gateway (LiteLLM Proxy)...")

        run_background = False
        final_proxy_args = []

        for arg in unknown_args:
            if arg in ["-d", "--detach"]:
                run_background = True
            else:
                final_proxy_args.append(arg)

        cmd = (
            litellm_exe_cmd
            + ["--port", "4000", "--telemetry", "False"]
            + final_proxy_args
        )

        if run_background:
            try:
                with open("gateway.log", "a") as outfile:
                    proc = subprocess.Popen(cmd, stdout=outfile, stderr=outfile)
                    with open("gateway.pid", "w") as pid_file:
                        pid_file.write(str(proc.pid))
                print("  ✅ Gateway started in background.")
                print("  📝 Logs: gateway.log")
                print("  ℹ️  To stop: kibo proxy stop")
            except Exception as e:
                print(f"❌ Failed to start Gateway in background: {e}")
        else:
            try:
                print("  ✅ Gateway listening at http://localhost:4000")
                print("  ⌨️  Press Ctrl+C to stop.")
                subprocess.run(cmd, check=True)
            except KeyboardInterrupt:
                print("\n🛑 Gateway stopped.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to start Gateway: {e}")

    elif args.proxy_action == "stop":
        print("🛑 Stopping Kibo Gateway...")
        try:
            import signal
            import psutil

            with open("gateway.pid", "r") as pid_file:
                pid = int(pid_file.read().strip())

            try:
                if os.name == "posix":
                    os.kill(pid, signal.SIGTERM)
                else:
                    psutil.Process(pid).terminate()
            except (ProcessLookupError, psutil.NoSuchProcess):
                print("⚠️ Process already stopped.")
            except (PermissionError, psutil.AccessDenied):
                print("❌ Permission denied when stopping process.")
                return

            os.remove("gateway.pid")
            print("✅ Gateway stopped.")

        except FileNotFoundError:
            print("⚠️ Gateway PID file not found. Is the gateway running?")
        except Exception as e:
            print(f"❌ Error stopping gateway: {e}")


def main():
    """
    Kibo CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="Kibo AI: Universal Distributed Agent Framework CLI",
        epilog="Use 'kibo <command> --help' for more information on a specific command.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="command", title="Commands", help="Action to perform"
    )

    start_examples = """Examples:
  kibo start db                        # Start ChromaDB service
  kibo start --head --port=6379        # Start a new Kibo Cluster Head Node
  kibo start --address='127.0.0.1:6379' # Join an existing cluster as a Worker
  kibo start --num-cpus=2              # Start with specific resources"""

    start_parser = subparsers.add_parser(
        "start",
        help="Start a Kibo node (Head or Worker) or a Service.",
        description="Starts the local runtime. By default starts a worker node connecting to localhost. Use --head to start a new cluster.",
        epilog=start_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    start_parser.add_argument(
        "service",
        nargs="?",
        choices=["db"],
        help="Optional service to start instead of a node (e.g., 'db' for ChromaDB).",
    )

    subparsers.add_parser(
        "start-all",
        help="Start the full platform (Head Node + Gateway).",
        description="Convenience command to launch both the Kibo Head Node and the API Gateway (Proxy).",
    )

    subparsers.add_parser(
        "stop",
        help="Stop the local Kibo node.",
        description="Stops any running Ray processes on this machine.",
    )

    status_examples = """Examples:
  kibo status                          # Show status of local connection
  kibo status --address='127.0.0.1:6379' # Show status of specific cluster"""

    subparsers.add_parser(
        "status",
        help="Show cluster status.",
        description="Displays the status of the Kibo/Ray cluster.",
        epilog=status_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    proxy_examples = """Examples:
  kibo proxy start                     # Start proxy in foreground on port 4000
  kibo proxy start -d                  # Start proxy in background (detached)
  kibo proxy start --config examples/proxy_config.yaml  # Start with custom config
  kibo proxy stop                      # Stop the running proxy"""

    proxy_parser = subparsers.add_parser(
        "proxy",
        help="Manage the Kibo Gateway (LiteLLM Proxy).",
        description="Controls the LiteLLM-based proxy server for unified model access.",
        epilog=proxy_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    proxy_subs = proxy_parser.add_subparsers(dest="proxy_action", required=True)

    p_start = proxy_subs.add_parser("start", help="Start the proxy server.")
    p_start.add_argument(
        "-d", "--detach", action="store_true", help="Run in background."
    )

    proxy_subs.add_parser("stop", help="Stop the proxy server.")

    mem_parser = subparsers.add_parser(
        "memory",
        help="Manage Kibo Memory (Mem0).",
        description="Interact with the semantic memory layer.",
    )
    mem_subs = mem_parser.add_subparsers(dest="mem_action", required=True)

    m_add = mem_subs.add_parser("add", help="Store a new memory.")
    m_add.add_argument("text", nargs="+", help="Content of the memory to store.")

    m_search = mem_subs.add_parser("search", help="Search existing memories.")
    m_search.add_argument("query", nargs="+", help="Query string.")

    mem_subs.add_parser("list", help="List all memories for the user.")

    serve_examples = """Examples:
  kibo serve my_agent.py               # Serve 'agent' from file on port 8000
  kibo serve ./src/agent.py --port 9000 # Custom port
  kibo serve my_agent.py --name my_crew # Serve specific variable 'my_crew'"""

    serve_parser = subparsers.add_parser(
        "serve",
        help="Serve an agent via HTTP (FastAPI).",
        description="Launch a lightweight FastAPI server to expose a local agent over HTTP.",
        epilog=serve_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    serve_parser.add_argument(
        "file", help="Path to the python file containing the agent."
    )
    serve_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host interface to bind to (default: 0.0.0.0).",
    )
    serve_parser.add_argument(
        "--port", type=int, default=8000, help="Port to listen on (default: 8000)."
    )
    serve_parser.add_argument(
        "--name", help="Name of the agent variable in the file (optional)."
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args, unknown = parser.parse_known_args()

    if args.command == "start":
        handle_start(args, unknown)
    elif args.command == "start-all":
        handle_start_all(args)
    elif args.command == "stop":
        handle_stop(args, unknown)
    elif args.command == "status":
        handle_status(args, unknown)
    elif args.command == "proxy":
        handle_proxy(args, unknown)
    elif args.command == "memory":
        handle_memory(args)
    elif args.command == "serve":
        handle_serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
