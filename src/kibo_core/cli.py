import sys
import subprocess
import shutil


def main():
    """
    Kibo CLI entry point.
    Wraps underlying distributed runtime commands (Ray) to provide a unified interface.
    """
    if len(sys.argv) < 2:
        print("Usage: kibo <command> [args]")
        print("Commands:")
        print("  start    Start a Kibo node (Head or Worker)")
        print("  start-all Start Kibo Head Node + Gateway (Proxy)")
        print("  stop     Stop the Kibo node")
        print("  status   Show cluster status")
        print("  proxy    Manage the Kibo Gateway (LiteLLM Proxy)")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "start":
        ray_executable = shutil.which("ray")
        if not ray_executable:
            print("Error: 'ray' executable not found. Please install dependencies.")
            sys.exit(1)

        print(" Starting Kibo Node...")

        start_flags = ["--disable-usage-stats"]

        if "--head" in args:
            start_flags.append("--include-dashboard=false")
            print("Initializing Kibo Cluster Coordinator (Head Node)...")
        else:
            print("Initializing Kibo Worker Node...")

        final_args = args + [f for f in start_flags if f not in args]

        cmd = [ray_executable, "start"] + final_args

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            for line in result.stdout.split("\n"):
                if "Local node IP" in line:
                    print(f"  {line.strip()}")

            print(" Kibo Node started successfully.")

            port = "6379"  # Default
            for i, arg in enumerate(args):
                if arg.startswith("--port="):
                    port = arg.split("=")[1]
                elif arg == "--port" and i + 1 < len(args):
                    port = args[i + 1]

            print("\nNext steps:")
            if "--head" in args:
                print(f"  To join a worker node to this cluster:")
                print(f"    kibo start --address='<THIS_IP>:{port}'")
            else:
                print(f"  To check cluster status:")
                print(f"    kibo status")

        except subprocess.CalledProcessError as e:
            print(f" Failed to start Kibo Node.")
            print(f"\n{e.stderr}")

            print("\nTroubleshooting tips:")
            print("1. If you see 'Address already in use', port 6379 might be busy.")
            print("   -> Try stopping old processes: 'kibo stop' or 'pkill -f ray'")
            print("   -> Or run on a different port: 'kibo start --head --port=6380'")
            print(
                "2. If you see connection errors, ensure the Head node IP is reachable."
            )
            sys.exit(e.returncode)

    elif command == "start-all":
        print("🚀 Launching Kibo AI Platform...")

        # Self-reference command
        kibo_cmd = [sys.executable, "-m", "kibo_core.cli"]

        # 1. Start Proxy (Background)
        print("\n[1/2] Starting Gateway...")
        proxy_cmd = kibo_cmd + [
            "proxy",
            "start",
            "--config",
            "examples/proxy_config.yaml",
            "-d",
        ]

        try:
            subprocess.run(proxy_cmd, check=True)
            print("✅ Gateway started.")
        except subprocess.CalledProcessError:
            print("❌ Failed to start Gateway.")
            sys.exit(1)

        # 2. Start Head Node
        print("\n[2/2] Starting Cluster Head Node...")
        node_cmd = kibo_cmd + ["start", "--head", "--port=6379"]

        try:
            subprocess.run(node_cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)

    elif command == "stop":
        ray_executable = shutil.which("ray")
        if not ray_executable:
            print("Error: 'ray' executable not found. Please install dependencies.")
            sys.exit(1)

        print(" Stopping Kibo Node...")
        cmd = [ray_executable, "stop"] + args
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(" Kibo Node stopped.")
        else:
            print(" Failed to stop Kibo Node.")
            if result.stderr:
                print(f"Error details:\n{result.stderr}")
            sys.exit(result.returncode)

    elif command == "status":
        ray_executable = shutil.which("ray")
        if not ray_executable:
            print("Error: 'ray' executable not found. Please install dependencies.")
            sys.exit(1)

        cmd = [ray_executable, "status"] + args
        subprocess.run(cmd)

    elif command == "proxy":
        if not args:
            print("Usage: kibo proxy [start|stop] [args]")
            sys.exit(1)

        subcmd = args[0]
        proxy_args = args[1:]

        litellm_executable = shutil.which("litellm")
        if not litellm_executable:
            litellm_executable = [sys.executable, "-m", "litellm"]
        else:
            litellm_executable = [litellm_executable]

        if subcmd == "start":
            print(" Starting Kibo Gateway (LiteLLM Proxy)...")

            # Check for background flag
            run_background = False
            if "-d" in proxy_args:
                proxy_args.remove("-d")
                run_background = True
            elif "--detach" in proxy_args:
                proxy_args.remove("--detach")
                run_background = True

            cmd = (
                litellm_executable
                + ["--port", "4000", "--telemetry", "False"]
                + proxy_args
            )

            if run_background:
                try:
                    # Run in background using Popen
                    with open("gateway.log", "a") as outfile:
                        subprocess.Popen(cmd, stdout=outfile, stderr=outfile)
                    print("  Gateway started in background.")
                    print("  Logs are being written to gateway.log")
                    print("  To stop: kibo proxy stop")
                except Exception as e:
                    print(f" Failed to start Gateway in background: {e}")
            else:
                try:
                    print("  Gateway listening at http://localhost:4000")
                    print("  Press Ctrl+C to stop.")
                    subprocess.run(cmd, check=True)
                except KeyboardInterrupt:
                    print("\n Gateway stopped.")
                except subprocess.CalledProcessError as e:
                    print(f" Failed to start Gateway.")
                    print(f"{e}")

        elif subcmd == "stop":
            print(" Stopping Kibo Gateway...")
            # Simple pkill for now (matches cli behavior of wrapping tools)
            try:
                subprocess.run(["pkill", "-f", "litellm"], check=False)
                print(" Gateway stopped.")
            except Exception as e:
                print(f" Error stopping gateway: {e}")

        else:
            print(f"Unknown proxy command: {subcmd}")
            print("Available proxy commands: start, stop")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, status, proxy")
        sys.exit(1)


if __name__ == "__main__":
    main()
