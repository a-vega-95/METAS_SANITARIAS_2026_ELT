import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'SRC'))

from config import PIV_FILE, DIR_REM_ACTUAL, DIR_REM_ANTERIOR

def check_environment():
    print("=== Verificación de Entorno ===")
    
    # 1. PIV File
    if os.path.exists(PIV_FILE):
        print(f"[OK] Archivo PIV encontrado: {PIV_FILE}")
    else:
        print(f"[ERROR] Archivo PIV NO encontrado: {PIV_FILE}")
        
    # 2. Directorios REM
    print(f"\nVerificando directorios REM:")
    for name, path in [("REM ACTUAL", DIR_REM_ACTUAL), ("REM ANTERIOR", DIR_REM_ANTERIOR)]:
        if os.path.exists(path):
            print(f"[OK] {name}: {path}")
            # Listar contenido brevemente
            try:
                files = os.listdir(path)
                print(f"    -> Contiene {len(files)} items.")
            except:
                pass
        else:
            print(f"[WARNING] {name} NO encontrado: {path}")
            
    print("\n=== Fin de Verificación ===")

if __name__ == "__main__":
    check_environment()
