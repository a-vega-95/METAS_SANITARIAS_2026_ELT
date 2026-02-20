import os
from datetime import datetime

# Años de Evaluación
AGNO_ACTUAL = 2026
AGNO_ANTERIOR = 2025

# Prevalencias (Res. Exenta N° 650)
PREVALENCIA_DM2 = 0.123 # 12.3%

# HTA Estraficada
PREVALENCIA_HTA_15_24 = 0.007 # 0.7%
PREVALENCIA_HTA_25_44 = 0.106 # 10.6%
PREVALENCIA_HTA_45_64 = 0.451 # 45.1%
PREVALENCIA_HTA_65_MAS = 0.733 # 73.3%

# Respiratorio
PREVALENCIA_ASMA = 0.10  # 10.0%
PREVALENCIA_EPOC = 0.117 # 11.7%

# Rutas Base
if os.environ.get("METAS_BASE_DIR"):
    BASE_DIR = os.environ["METAS_BASE_DIR"]
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
DATOS_DIR = os.path.join(BASE_DIR, "DATOS")
ENTRADA_DIR = os.path.join(DATOS_DIR, "ENTRADA")

# Rutas Dinámicas
# Se asume estructura: DATOS/ENTRADA/REM_ANO_X/SERIE_Y
DIR_REM_ACTUAL = os.path.join(ENTRADA_DIR, "REM_ANO_ACTUAL")
DIR_REM_ANTERIOR = os.path.join(ENTRADA_DIR, "REM_ANO_PASADO")

DIR_SERIE_A_ACTUAL = os.path.join(DIR_REM_ACTUAL, "SERIE_A")
DIR_SERIE_A_ANTERIOR = os.path.join(DIR_REM_ANTERIOR, "SERIE_A")

DIR_SERIE_P_ACTUAL = os.path.join(DIR_REM_ACTUAL, "SERIE_P")
DIR_SERIE_P_ANTERIOR = os.path.join(DIR_REM_ANTERIOR, "SERIE_P")

PIV_FILE = os.path.join(DATOS_DIR, "PIV", "PIV_2024_09_DSM_SI_ACEPTADOS.parquet")
