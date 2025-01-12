import logging
import os

def setup_logger(name="kibo"):
    """
    Configures a Kibo-branded logger.
    """
    if os.getenv("KIBO_LOG_LEVEL"):
        level = getattr(logging, os.getenv("KIBO_LOG_LEVEL").upper())
    else:
        level = logging.INFO

    logging.basicConfig(format='%(asctime)s [%(levelname)s] [Kibo] %(message)s', level=level)
    return logging.getLogger(name)

def silence_ray_logs():
    """
    Silences Ray's default noisy logging and specific warnings.
    """
    import os
    import warnings
    
    # Ray uses these env vars to control logging
    os.environ["RAY_USAGE_STATS_ENABLED"] = "0"
    os.environ["RAY_NO_PROMETHEUS"] = "1"
    os.environ["RAY_ACCEL_ENV_VAR_OVERRIDE_ON_ZERO"] = "0" # Fixes the FutureWarning
    
    # Filter out specific FutureWarnings from Ray
    warnings.filterwarnings("ignore", category=FutureWarning, module="ray")
    
import logging
    
class FilterRayLogs(logging.Filter):
    def filter(self, record):
        if "ray" in record.getMessage().lower():
            # Replace 'ray' with 'kibo-runtime' in log messages
            record.msg = record.msg.replace("ray", "kibo-runtime").replace("Ray", "Kibo Runtime")
        return True
