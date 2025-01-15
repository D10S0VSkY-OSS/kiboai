import ray
import logging
from kibo_core.utils.logging import silence_ray_logs

def kibo_init(address: str = None, **kwargs):
    """
    Initialize Kibo Distributed Runtime.
    """
    silence_ray_logs()
    print("Initializing Kibo Runtime...")

    # Default to reducing Ray log noise
    if "logging_level" not in kwargs:
        kwargs["logging_level"] = logging.ERROR
        
    # Agresively silence worker logs via runtime_env if not provided
    if "runtime_env" not in kwargs:
        kwargs["runtime_env"] = {}
    
    if "env_vars" not in kwargs["runtime_env"]:
        kwargs["runtime_env"]["env_vars"] = {}

    # This disables the worker startup logs
    kwargs["runtime_env"]["env_vars"]["RAY_DEDUP_LOGS"] = "0"
    kwargs["runtime_env"]["configure_logging"] = False 
    kwargs["log_to_driver"] = False
    
    # Check if we are already connected
    if ray.is_initialized():
        print("Kibo Runtime is already active.")
        return ray.get_runtime_context()

    # 1. Respect RAY_ADDRESS if set explicitly in environment (Standard Ray behavior)
    # This allows connecting to Docker/Remote clusters via ray://localhost:10001
    import os
    env_address = os.environ.get("RAY_ADDRESS")
    if address is None and env_address:
        print(f"Connecting to Kibo Cluster at {env_address} (from RAY_ADDRESS)...")
        
        # Ray Client (ray://) has strict limitations on runtime_env interaction 
        # specifically when the server is already running in a container with its own paths (/app).
        # We strip potentially conflicting env configs for client connections.
        client_kwargs = kwargs.copy()
        if env_address.startswith("ray://"):
            # Avoid re-declaring env_vars that might conflict with server-side immutable configs
             if "runtime_env" in client_kwargs:
                 # Just use an empty runtime env for client to avoid "/app" path conflicts or similar
                 # The server environment (Docker) is already fully provisioned.
                 del client_kwargs["runtime_env"]

        try:
            return ray.init(address=env_address, ignore_reinit_error=True, **client_kwargs)
        except Exception as e:
            # Fallback trying without runtime_env if needed, although we already cleaned it.
            # But sometimes even Ray Client itself tries to sync things.
            # However, if this fails, we probably shouldn't auto-fallback to local ephemeral, 
            # because the user explicitly asked for RAY_ADDRESS.
            print(f"⚠️ Failed to connect to {env_address}: {e}")
            raise e


    # 2. Try 'auto' first if no address specified, to connect to existing local cluster
    if address is None:
        try:
            # Try to connect to an existing cluster (started via `kibo start`)
            res = ray.init(address='auto', ignore_reinit_error=True, **kwargs)
            print(f"✅ Connected to Kibo Cluster at {res.address_info.get('address', 'unknown')}")
            return res
        except ConnectionError:
            print("⚠️ No existing Kibo Cluster found.") 
            # Fallback to local
        except Exception:
            # Fallback for other errors during auto-connect
            pass
            
    # If we are here, auto failed or address was specific
    if address is None:
        print("Starting local ephemeral instance...")
        try:
            res = ray.init(ignore_reinit_error=True, **kwargs)
            print("✅ Local Kibo Instance started.")
            return res
        except Exception as e:
            print(f"Error starting local Kibo instance: {e}")
            raise
    else:
        # User specified address
        return ray.init(address=address, ignore_reinit_error=True, **kwargs)

def get(object_ref):
    """
    Get a remote object or a list of remote objects from the object store.
    Wrapper around ray.get().
    """
    return ray.get(object_ref)
