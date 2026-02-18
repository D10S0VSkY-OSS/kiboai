try:
    import ray

    RAY_AVAILABLE = True
except ImportError:
    ray = None
    RAY_AVAILABLE = False

import logging
from kibo_core.shared_kernel.logging import silence_ray_logs

_DISTRIBUTED_MODE = False


def kibo_init(address: str = None, distributed_execution: bool = False, **kwargs):
    """
    Initialize Kibo Distributed Runtime.
    :param distributed_execution: If True, connects to or starts a distributed runtime.
                                  If False, runs in local mode (no cluster). Default is False.
    """
    global _DISTRIBUTED_MODE
    _DISTRIBUTED_MODE = distributed_execution

    if not distributed_execution:
        print("Running in LOCAL mode (Distributed execution disabled).")
        return None

    if not RAY_AVAILABLE:
        raise ImportError(
            "Ray is not installed. Please install 'kiboai[ray]' to use distributed execution."
        )

    silence_ray_logs()
    print("Initializing Kibo Runtime...")

    # Kibo Runtime Initialization
    if "logging_level" not in kwargs:
        kwargs["logging_level"] = logging.ERROR

    if "runtime_env" not in kwargs:
        kwargs["runtime_env"] = {}

    if "env_vars" not in kwargs["runtime_env"]:
        kwargs["runtime_env"]["env_vars"] = {}

    # 1. Hide internal Ray warnings
    kwargs["runtime_env"]["env_vars"]["RAY_DEDUP_LOGS"] = "0"
    kwargs["runtime_env"]["env_vars"]["UV_LINK_MODE"] = "copy"

    # 3. Kibo-specific: Disable METRICS agent entirely to stop "exporter agent" errors in console
    # This disables the Prometheus exporter which causes the RpcError code: 14 loops when Dashboard is off.
    # Set these globally for the driver process too
    import os

    os.environ["RAY_enable_metrics_collection"] = "0"
    os.environ["RAY_disable_metrics_collection"] = "1"

    kwargs["runtime_env"]["env_vars"]["RAY_enable_metrics_collection"] = "0"
    kwargs["runtime_env"]["env_vars"][
        "RAY_disable_metrics_collection"
    ] = "1"  # Redundant safety
    kwargs["runtime_env"]["env_vars"]["RAY_USAGE_STATS_ENABLED"] = "0"

    # 2. Prevent Ray from re-creating expensive venvs if we are sharing the same env
    # (Checking if we are inside a UV/Venv environment)
    import os

    if "VIRTUAL_ENV" in os.environ:
        # Force workers to inherit the current environment instead of rebuilding it
        # This silences "(raylet) Creating virtual environment..."
        kwargs["runtime_env"]["env_vars"]["VIRTUAL_ENV"] = os.environ["VIRTUAL_ENV"]
        # We might need to trick Ray into thinking it doesn't need to rebuild

    kwargs["log_to_driver"] = False
    kwargs["configure_logging"] = (
        True  # Let python logging handle it, don't let Ray hijack stdout/stderr arbitrarily
    )

    if "include_dashboard" not in kwargs:
        kwargs["include_dashboard"] = False  # Explicitly disable dashboard

    if ray.is_initialized():
        print("Kibo Runtime is already active.")
        return ray.get_runtime_context()

    import os

    env_address = os.environ.get("RAY_ADDRESS")
    if address is None and env_address:
        print(f"Connecting to Kibo Cluster at {env_address} (from RAY_ADDRESS)...")

        client_kwargs = kwargs.copy()
        if env_address.startswith("ray://"):
            if "runtime_env" in client_kwargs:
                del client_kwargs["runtime_env"]

        try:
            return ray.init(
                address=env_address, ignore_reinit_error=True, **client_kwargs
            )
        except Exception as e:
            print(f" Failed to connect to {env_address}: {e}")
            raise e

    if address is None:
        try:
            res = ray.init(address="auto", ignore_reinit_error=True, **kwargs)
            print(
                f" Connected to Kibo Cluster at {res.address_info.get('address', 'unknown')}"
            )
            return res
        except ConnectionError:
            print(" No existing Kibo Cluster found.")
        except Exception:
            pass

    if address is None:
        print("Starting local ephemeral instance...")
        try:
            res = ray.init(ignore_reinit_error=True, **kwargs)
            print(" Local Kibo Instance started.")
            return res
        except Exception as e:
            print(f"Error starting local Kibo instance: {e}")
            raise
    else:
        return ray.init(address=address, ignore_reinit_error=True, **kwargs)


def get(object_ref, **kwargs):
    """
    Get a remote object or a list of remote objects from the object store.
    Wrapper around ray.get().
    If distributed mode is disabled, returns object_ref immediately assuming it's the result.
    If object_ref is a concurrent.futures.Future, waits for its result.
    """
    if not _DISTRIBUTED_MODE:
        from concurrent.futures import Future

        if isinstance(object_ref, Future):
            return object_ref.result()
        return object_ref

    return ray.get(object_ref, **kwargs)
