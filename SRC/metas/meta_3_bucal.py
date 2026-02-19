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

def calcular_meta_3():
    print("=== Calculando Meta 3: Salud Bucal ===")
    
    # 1. Configuración
    DATA_DIR = r"DATOS\ENTRADA\SERIE_A"
    PIV_FILE = r"DATOS\PIV\PIV_MASTER_GOLD_2025_09_ACEPTADOS.parquet"
    
    # Meta 3A: CERO (0-9 años)
    # Num: REM A03, Sección D.7.
    # Den: PIV 0-9 años.
    
    SHEET_3A = "A03"
    # Placeholder cells for 3A numerator (need valid cells from user or logica)
    # Assuming D7 section total involves specific cells.
    # I'll use a placeholder variable or empty list if unknown, but better to try.
    # LOGICA doesn't specify cells.
    CELLS_3A = [] # Placeholder
    
    # Meta 3B: Caries (6 años)
    # Num: REM A09, Sección C. S48 + T48.
    SHEET_3B = "A09"
    CELLS_3B = ["S48", "T48"]
    
    # 2. Cargar Datos
    try:
        mapping = scan_rem_files(DATA_DIR)
        piv_data = load_piv_data(PIV_FILE)
        print(f"Cargados {len(mapping)} archivos REM y {len(piv_data)} registros PIV.")
    except Exception as e:
        print(f"Error fatal cargando datos: {e}")
        return

    # 3. Procesar Denominadores (PIV)
    # Agrupar por Centro
    denominadores = {} # {cod_centro: {'3A': count, '3B': count}}
    
    for row in piv_data:
        centro = row.get('COD_CENTRO', '')
        edad = row.get('EDAD_EN_FECHA_CORTE')
        if edad is None: edad = -1
        estado = row.get('ACEPTADO_RECHAZADO', '')
        
        if estado != 'ACEPTADO':
            continue
            
        if centro not in denominadores:
            denominadores[centro] = {'3A': 0, '3B': 0}
            
        # 3A: 0-9 años
        if 0 <= edad <= 9:
            denominadores[centro]['3A'] += 1
            
        # 3B: 6 años
        if edad == 6:
            denominadores[centro]['3B'] += 1

    # 4. Procesar Numeradores (REM)
    reporte = []
    
    numeradores = {} # {cod_centro: {'3A': 0, '3B': 0}}
    
    for entry in mapping:
        raw_code = entry['code']
        # Normalize code
        real_code = raw_code
        if raw_code[-1].isalpha() and raw_code[:-1].isdigit():
             real_code = raw_code[:-1]
             
        file_path = entry['path']
        
        if real_code not in numeradores:
            numeradores[real_code] = {'3A': 0, '3B': 0}
            
        if not os.path.exists(file_path):
            continue
            
        try:
             wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
             
             # 3B Numerator (A09 S48+T48)
             if SHEET_3B in wb.sheetnames:
                 sheet = wb[SHEET_3B]
                 for cell in CELLS_3B:
                     val = sheet[cell].value
                     if val and isinstance(val, (int, float)):
                         numeradores[real_code]['3B'] += val
                         
             # 3A Numerator (A03 D.7?)
             if SHEET_3A in wb.sheetnames and CELLS_3A:
                 sheet = wb[SHEET_3A]
                 for cell in CELLS_3A:
                     val = sheet[cell].value
                     if val and isinstance(val, (int, float)):
                         numeradores[real_code]['3A'] += val
             
             wb.close()
        except:
             pass

    # 5. Generar Reporte Combinado
    all_centers = set(denominadores.keys()) | set(numeradores.keys())
    
    for code in all_centers:
        den = denominadores.get(code, {'3A': 0, '3B': 0})
        num = numeradores.get(code, {'3A': 0, '3B': 0})
        
        # 3A Report
        den_3a = den['3A']
        num_3a = num['3A']
        cump_3a = (num_3a / den_3a * 100) if den_3a > 0 else 0
        
        reporte.append({
            'Centro': code, 'Meta_ID': 'Meta 3A', 'Indicador': 'Odontológico CERO',
            'Numerador': num_3a, 'Denominador': den_3a, 'Cumplimiento': cump_3a,
            'Meta_Fijada': 48.0, 'Meta_Nacional': 48.0
        })
        
        # 3B Report
        den_3b = den['3B']
        num_3b = num['3B']
        cump_3b = (num_3b / den_3b * 100) if den_3b > 0 else 0
        
        reporte.append({
            'Centro': code, 'Meta_ID': 'Meta 3B', 'Indicador': 'Caries 6 años',
            'Numerador': num_3b, 'Denominador': den_3b, 'Cumplimiento': cump_3b,
            'Meta_Fijada': 21.0, 'Meta_Nacional': 22.0
        })
    
    # Output
    output_path = normalize_path(r"DATOS\reporte_meta_3_preliminar.csv")
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Centro', 'Meta_ID', 'Indicador', 'Numerador', 'Denominador', 'Cumplimiento', 'Meta_Fijada', 'Meta_Nacional'])
            writer.writeheader()
            for r in reporte:
                writer.writerow({
                    'Centro': r['Centro'],
                    'Meta_ID': r['Meta_ID'],
                    'Indicador': r['Indicador'],
                    'Numerador': r['Numerador'],
                    'Denominador': r['Denominador'],
                    'Cumplimiento': r['Cumplimiento'],
                    'Meta_Fijada': r['Meta_Fijada'],
                    'Meta_Nacional': r['Meta_Nacional']
                })
        print(f"Reporte guardado en {output_path}")
    except:
        pass

if __name__ == "__main__":
    calcular_meta_3()
