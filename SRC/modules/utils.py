import os
import sys
import csv
import logging
from datetime import datetime

def get_project_root():
    """Returns the root directory of the project."""
    if os.environ.get("METAS_BASE_DIR"):
        return os.environ["METAS_BASE_DIR"]
    # Assuming this file is in SRC/modules/
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def normalize_path(path):
    """Normalizes a path to be absolute and use correct separators."""
    if not os.path.isabs(path):
        path = os.path.join(get_project_root(), path)
    return os.path.normpath(path)

def setup_audit_logger():
    """Configures and returns the audit logger."""
    log_dir = normalize_path("LOG")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    log_file = os.path.join(log_dir, f"MET_SANIT_{timestamp}.LOG")
    
    # Create a custom logger
    logger = logging.getLogger("audit_logger")
    logger.setLevel(logging.INFO)
    
    # handlers
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    console_handler = logging.StreamHandler(sys.stdout)
    
    # format
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Avoid adding handlers multiple times if function is called repeatedly
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

def load_center_names():
    """Carga los nombres de los centros desde DOC/COD_CENTROS_SALUD.CSV"""
    mapping_names = {}
    csv_path = normalize_path("DOC/COD_CENTROS_SALUD.CSV")
    
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row['COD_CENTRO'].strip()
                    name = row['NOMBRE'].strip()
                    mapping_names[code] = name
                    if code[-1].isalpha():
                        mapping_names[code[:-1]] = name
        except Exception as e:
            print(f"Error cargando nombres de centros: {e}")
    return mapping_names
