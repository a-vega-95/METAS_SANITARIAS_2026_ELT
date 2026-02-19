import sys
import os
import csv
import openpyxl
import pyarrow.parquet as pq

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'SRC'))

from modules.dataloaders import scan_rem_files, load_piv_data
from modules.utils import normalize_path

def calcular_meta_2():
    print("=== Calculando Meta 2: Papanicolaou (PAP) o Test VPH ===")
    
    # 1. Configuración
    DATA_DIR = r"DATOS\ENTRADA\SERIE_P"
    PIV_FILE = r"DATOS\PIV\PIV_MASTER_GOLD_2025_09_ACEPTADOS.parquet"
    
    # Lógica Meta 2:
    SHEET_P12 = "P12"
    COLS_REM = ['B', 'C']
    ROWS_REM = range(11, 19) # 11 to 18 inclusive
    
    # 2. Cargar Datos
    try:
        mapping = scan_rem_files(DATA_DIR)
        piv_data = load_piv_data(PIV_FILE)
        print(f"Cargados {len(mapping)} archivos REM P y {len(piv_data)} registros PIV.")
    except Exception as e:
        print(f"Error fatal cargando datos: {e}")
        return

    # 3. Procesar Denominadores (PIV)
    denominadores = {} # {cod_centro: count}
    
    for row in piv_data:
        centro = row.get('COD_CENTRO', '')
        edad = row.get('EDAD_EN_FECHA_CORTE')
        if edad is None: edad = -1
        estado = row.get('ACEPTADO_RECHAZADO', '')
        genero = row.get('GENERO', '') 
        
        if estado != 'ACEPTADO':
            continue
            
        if 25 <= edad <= 64:
            # Filter Logic: "Personas". User notes say "Test VPH o PAP vigente en personas...".
            # Usually strict filter for women (MUJER) or inclusive. 
            # I will filter by Female or check Genero Normalized to be safe as previously decided.
            if 'MUJER' in str(genero).upper() or 'FEMENINO' in str(row.get('GENERO_NORMALIZADO', '')).upper():
                if centro not in denominadores:
                    denominadores[centro] = 0
                denominadores[centro] += 1

    # 4. Procesar Numeradores (REM P12)
    numeradores = {} # {cod_centro: 0}
    
    for entry in mapping:
        raw_code = entry['code']
        real_code = raw_code
        if raw_code[-1].isalpha() and raw_code[:-1].isdigit():
             real_code = raw_code[:-1]
             
        file_path = entry['path']
        
        if real_code not in numeradores:
            numeradores[real_code] = 0
            
        if not os.path.exists(file_path):
            continue
            
        try:
             wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
             
             if SHEET_P12 in wb.sheetnames:
                 sheet = wb[SHEET_P12]
                 
                 for col in COLS_REM:
                     for row_idx in ROWS_REM:
                         cell = f"{col}{row_idx}"
                         val = sheet[cell].value
                         if val and isinstance(val, (int, float)):
                             numeradores[real_code] += val
                             
             wb.close()
        except Exception as e:
             print(f"Error procesando {raw_code}: {e}")

    # 5. Generar Reporte
    all_centers = set(denominadores.keys()) | set(numeradores.keys())
    reporte = []
    
    total_num = 0
    total_den = 0
    
    for code in all_centers:
        den = denominadores.get(code, 0)
        num = numeradores.get(code, 0)
        
        cumplimiento = (num / den * 100) if den > 0 else 0
        
        total_num += num
        total_den += den
        
        reporte.append({
            'Centro': code,
            'Numerador': num,
            'Denominador': den,
            'Cumplimiento': cumplimiento
        })

    cumplimiento_global = (total_num / total_den * 100) if total_den > 0 else 0
    
    print("\n=== RESULTADOS GLOBALES META 2 (PAP/VPH) ===")
    print(f"Numerador Total: {total_num}")
    print(f"Denominador Total (Mujeres 25-64): {total_den}")
    print(f"Cumplimiento Actual: {cumplimiento_global:.2f}%")
    print(f"Meta Fijada: 63.0%")
    
    # Output
    output_path = normalize_path(r"DATOS\reporte_meta_2_preliminar.csv")
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Centro', 'Numerador', 'Denominador', 'Cumplimiento'])
            writer.writeheader()
            writer.writerows(reporte)
        print(f"Reporte guardado en {output_path}")
    except:
        pass

if __name__ == "__main__":
    calcular_meta_2()
