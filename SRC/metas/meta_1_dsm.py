import sys
import os
import csv
import openpyxl

# Add project root to path to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'SRC'))

from modules.dataloaders import scan_rem_files, get_rem_value
from modules.utils import normalize_path

def calcular_meta_1():
    print("=== Calculando Meta 1: Recuperación del Desarrollo Psicomotor ===")
    
    # 1. Configuración
    DATA_DIR = r"DATOS\ENTRADA\SERIE_A"
    TARGET_SHEET = "A03"
    
    # Coordenadas según LOGICA_NEGOCIO.txt
    COLS = ['J', 'K', 'L', 'M']
    ROW_NUM = 26
    ROW_DEN = 23
    
    # 2. Cargar Mapeo (Escaneo de Archivos)
    try:
        mapping = scan_rem_files(DATA_DIR)
        print(f"Se encontraron {len(mapping)} archivos REM en {DATA_DIR}.")
    except Exception as e:
        print(f"Error fatal escaneando archivos: {e}")
        return

    reporte = []
    
    # Estructura para acumular por centro
    # centros[code] = {'num': 0, 'den': 0}
    centros = {}

    for entry in mapping:
        code = entry['code']
        file_path = entry['path']
        filename = entry['filename']
        year = entry['year']
        month = entry['month']
        
        if code not in centros:
            centros[code] = {'num': 0, 'den': 0}
            
        if not os.path.exists(file_path):
            continue
            
        # Lógica de Fechas (Lag)
        # Numerador: Enero a Diciembre 2026
        is_numerator_period = (year == 2026)
        
        # Denominador: Octubre 2025 a Septiembre 2026
        is_denominator_period = False
        if year == 2025 and month and month >= 10:
            is_denominator_period = True
        elif year == 2026 and month and month <= 9:
            is_denominator_period = True
            
        if not is_numerator_period and not is_denominator_period:
            continue

        num_local = 0
        den_local = 0
        
        try:
             wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
             if TARGET_SHEET in wb.sheetnames:
                 sheet = wb[TARGET_SHEET]
                 
                 # Si corresponde al periodo del Numerador
                 if is_numerator_period:
                     for col in COLS:
                         cell = f"{col}{ROW_NUM}"
                         val = sheet[cell].value
                         if val and isinstance(val, (int, float)):
                             num_local += val
                             
                 # Si corresponde al periodo del Denominador
                 if is_denominator_period:
                     for col in COLS:
                         cell = f"{col}{ROW_DEN}"
                         val = sheet[cell].value
                         if val and isinstance(val, (int, float)):
                             den_local += val
                         
             wb.close()
        except Exception as e:
             print(f"Error procesando {filename}: {e}")
             continue
            
        centros[code]['num'] += num_local
        centros[code]['den'] += den_local
        
        # Debug info
        # print(f"Procesado {filename} (Mes:{month} Año:{year}): Num={num_local if is_numerator_period else 0}, Den={den_local if is_denominator_period else 0}")
    
    # Generar reporte final
    total_num = 0
    total_den = 0
    
    for code, data in centros.items():
        num = data['num']
        den = data['den']
        total_num += num
        total_den += den
        
        cumplimiento = (num / den * 100) if den > 0 else 0
        
        reporte.append({
            'Centro': code,
            'Periodo': '2026',
            'Numerador': num,
            'Denominador': den,
            'Cumplimiento': cumplimiento
        })

    # 4. Resultado Final Global
    cumplimiento_global = (total_num / total_den * 100) if total_den > 0 else 0
    
    print("\n=== RESULTADOS GLOBALES META 1 ===")
    print(f"Numerador Total (Recuperados): {total_num}")
    print(f"Denominador Total (Riesgo): {total_den}")
    print(f"Cumplimiento Actual: {cumplimiento_global:.2f}%")
    print(f"Meta Fijada: 90.0%")
    
    # Guardar reporte
    output_path = normalize_path(r"DATOS\reporte_meta_1_preliminar.csv")
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Centro', 'Periodo', 'Numerador', 'Denominador', 'Cumplimiento'])
            writer.writeheader()
            writer.writerows(reporte)
        print(f"Reporte detallado guardado en: {output_path}")
    except Exception as e:
        print(f"Error escribiendo reporte: {e}")

if __name__ == "__main__":
    calcular_meta_1()
