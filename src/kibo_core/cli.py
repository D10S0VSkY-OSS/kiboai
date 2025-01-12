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
        print("  stop     Stop the Kibo node")
        print("  status   Show cluster status")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    ray_executable = shutil.which("ray")
    if not ray_executable:
        print("Error: 'ray' executable not found. Please install dependencies.")
        sys.exit(1)

    if command == "start":
        # kibo start --head ... -> ray start --head ...
        print("🚀 Starting Kibo Node...")
        
        # Enforce silent startup flags to hide Ray branding where possible
        start_flags = ["--disable-usage-stats"]
        
        # Only include dashboard flag if it IS the head node, otherwise Ray complains
        if "--head" in args:
             start_flags.append("--include-dashboard=false")
             print("Initializing Kibo Cluster Coordinator (Head Node)...")
        else:
             print("Initializing Kibo Worker Node...")
        
        # Only add if not already present in user args to avoid duplicates
        final_args = args + [f for f in start_flags if f not in args]
        
        cmd = [ray_executable, "start"] + final_args
        
        # print(f"DEBUG: Executing {' '.join(cmd)}")
        
        try:
            # Capture output to suppress Ray branding/welcome message
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # We still want to show the Local IP if Ray reported it
            for line in result.stdout.split('\n'):
                if "Local node IP" in line:
                    print(f"ℹ️  {line.strip()}")

            print("✅ Kibo Node started successfully.")
            
            if "--head" in args:
                # Custom Kibo instructions instead of Ray's
                port = "6379" # Default
                for arg in args:
                    if arg.startswith("--port="):
                         port = arg.split("=")[1]
                
                print("\nNext steps:")
                print(f"  To join a worker node to this cluster:")
                print(f"    kibo start --address='<THIS_IP>:{port}'")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start Kibo Node.")
            # If it failed, show why (stderr)
            print(f"\n{e.stderr}")
            
            print("\nTroubleshooting tips:")
            print("1. If you see 'Address already in use', port 6379 might be busy.")
            print("   -> Try stopping old processes: 'kibo stop' or 'pkill -f ray'")
            print("   -> Or run on a different port: 'kibo start --head --port=6380'")
            print("2. If you see connection errors, ensure the Head node IP is reachable.")
            sys.exit(e.returncode)

    elif command == "stop":
        print("🛑 Stopping Kibo Node...")
        cmd = [ray_executable, "stop"] + args
        # Suppress output to hide "Stopped all X Ray processes"
        subprocess.run(cmd, capture_output=True)
        print("✅ Kibo Node stopped.")

    elif command == "status":
        cmd = [ray_executable, "status"] + args
        subprocess.run(cmd)

    elif command == "proxy":
        # Handle LiteLLM Proxy commands
        if not args:
            print("Usage: kibo proxy [start|stop] [args]")
            sys.exit(1)
        
        subcmd = args[0]
        proxy_args = args[1:]
        
        litellm_executable = shutil.which("litellm")
        if not litellm_executable:
            # Fallback to python -m litellm if executable not in path but module installed
            litellm_executable = [sys.executable, "-m", "litellm"]
        else:
            litellm_executable = [litellm_executable]

        if subcmd == "start":
            print("🌐 Starting Kibo Gateway (LiteLLM Proxy)...")
            # Default port 4000
            cmd = litellm_executable + ["--port", "4000", "--telemetry", "False"] + proxy_args
            
            try:
                # Run in foreground or detached? 
                # For a CLI 'start' usually implies a daemon or blocking. 
                # Let's run blocking for now so user can see logs, or they can use nohup etc.
                # But Kibo start (ray) runs as daemon. 
                # LiteLLM doesn't have a native daemon mode flag easily accessible here without more work.
                # We will run it and print instruction to use Ctrl+C or run in background.
                print("ℹ️  Gateway listening at http://localhost:4000")
                print("ℹ️  Press Ctrl+C to stop.")
                subprocess.run(cmd, check=True)
            except KeyboardInterrupt:
                print("\n🛑 Gateway stopped.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to start Gateway.")
                print(f"{e}")
                
        elif subcmd == "stop":
            print("🛑 To stop the Gateway, simply press Ctrl+C in the terminal where it's running.")
            print("   (Process management for the gateway is not yet daemonized in this version)")
            
        else:
            print(f"Unknown proxy command: {subcmd}")

    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, status, proxy")
        sys.exit(1)

if __name__ == "__main__":
    main()
