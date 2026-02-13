import logging
import os


def setup_logger(name="kibo"):
    """
    Configures a Kibo-branded logger.
    """
    log_level_str = os.getenv("KIBO_LOG_LEVEL", "").upper()
    level = getattr(logging, log_level_str, None)
    if level is None or not isinstance(level, int):
        level = logging.INFO

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] [Kibo] %(message)s", level=level
    )
    return logging.getLogger(name)

# Expose a default logger instance
logger = setup_logger()
on_worker = False

def silence_ray_logs():
    """
    Silences Ray's default noisy logging and specific warnings.
    """
    import os
    import warnings

    os.environ["RAY_USAGE_STATS_ENABLED"] = "0"
    os.environ["RAY_NO_PROMETHEUS"] = "1"
    os.environ["RAY_ACCEL_ENV_VAR_OVERRIDE_ON_ZERO"] = "0"  # Fixes the FutureWarning

    warnings.filterwarnings("ignore", category=FutureWarning, module="ray")


class FilterRayLogs(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if "ray" in msg.lower():
            import re

            sanitized = re.sub(r"\bray\b", "kibo-runtime", msg, flags=re.IGNORECASE)
            sanitized = re.sub(r"\bRay\b", "Kibo Runtime", sanitized)
            record.msg = sanitized
            record.args = ()  # Clear args since message is now pre-formatted
        return True
