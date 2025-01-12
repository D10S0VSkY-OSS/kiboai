import ray
import os
import sys

# Forzamos una limpieza de logs por si acaso interfiere
# os.environ["RAY_DEDUP_LOGS"] = "0"

print(f"Connecting to ray://localhost:10001 from {os.getcwd()}...")

try:
    # Intento 1: Con working_dir explícito al directorio actual (lo standard para cliente)
    # Esto debería causar que Ray empaquete el dir actual y lo mande a Docker.
    # Si falla con '/app', entonces es muy raro.
    res = ray.init("ray://localhost:10001", runtime_env={"working_dir": "."})
    
    print("✅ Connected!")
    print(f"Cluster resources: {ray.cluster_resources()}")
    
    @ray.remote
    def f():
        import os
        return f"Hello from {os.uname().nodename} (cwd: {os.getcwd()})"
        
    print(ray.get(f.remote()))

except Exception as e:
    print(f"❌ Failed: {e}")
