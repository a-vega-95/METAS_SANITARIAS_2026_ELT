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

def calcular_meta_7():
    print("=== Calculando Meta 7: Enfermedades Respiratorias (Asma/EPOC) ===")
    
    # 1. Configuración
    DATA_DIR = r"DATOS\ENTRADA\SERIE_P"
    PIV_FILE = r"DATOS\PIV\PIV_MASTER_GOLD_2025_09_ACEPTADOS.parquet"
    
    # Estimación Prevalencia
    # Asumimos 10% prevalencia combinada asma/epoc como placeholder si no hay datos exactos.
    PREVALENCIA_RESP = 0.10 
    
    # Numerador: REM P04
    # Placeholder cells for Asma/EPOC compensados (Sección Numérica)
    SHEET = "P04"
    CELLS = ["C15", "C16"] # Examples
    
    try:
        mapping = scan_rem_files(DATA_DIR)
        piv_data = load_piv_data(PIV_FILE)
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return

    # 1. Denominadores (Estimados)
    poblacion_target = {}
    for row in piv_data:
        centro = row.get('COD_CENTRO', '')
        edad = row.get('EDAD_EN_FECHA_CORTE')
        if edad is None: edad = -1
        estado = row.get('ACEPTADO_RECHAZADO', '')
        
        # Filtro basico: Aceptado y edad relevante (mayor de 5 para asma, 40 epoc)
        if estado == 'ACEPTADO' and edad >= 5:
            if centro not in poblacion_target: poblacion_target[centro] = 0
            poblacion_target[centro] += 1
            
    denominadores = {k: round(v * PREVALENCIA_RESP) for k, v in poblacion_target.items()}
    
    # 2. Numeradores (REM P04)
    numeradores = {}
    
    for entry in mapping:
        raw_code = entry['code']
        real_code = raw_code
        if raw_code[-1].isalpha() and raw_code[:-1].isdigit():
             real_code = raw_code[:-1]
             
        file_path = entry['path']
        
        if real_code not in numeradores:
            numeradores[real_code] = 0
            
        if not os.path.exists(file_path): continue
        
        try:
             wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
             if SHEET in wb.sheetnames:
                 sheet = wb[SHEET]
                 for cell in CELLS:
                     val = sheet[cell].value
                     if val and isinstance(val, (int, float)):
                         numeradores[real_code] += val
             wb.close()
        except: pass

    # Reporte
    all_centers = set(denominadores.keys()) | set(numeradores.keys())
    reporte = []
    
    total_num = 0
    total_den = 0
    
    for c in all_centers:
        num = numeradores.get(c, 0)
        den = denominadores.get(c, 0)
        cump = (num/den*100) if den > 0 else 0
        
        total_num += num
        total_den += den
        
        reporte.append({
            'Centro': c, 
            'Meta_ID': 'Meta 7',
            'Indicador': 'Cobertura Respiratoria',
            'Numerador': num, 
            'Denominador': den, 
            'Cumplimiento_Actual': cump,
            'Meta_Fijada': 16.77,
            'Meta_Nacional': 20.0
        })
        
    print("\n=== RESULTADOS GLOBALES META 7 (RESP) ===")
    print(f"Numerador: {total_num}")
    print(f"Denominador: {total_den}")
    if total_den > 0:
        print(f"Cumplimiento: {total_num/total_den*100:.2f}%")
        
    # Guardar reporte
    output_path = normalize_path(r"DATOS\reporte_meta_7_preliminar.csv")
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
                    'Cumplimiento': r['Cumplimiento_Actual'],
                    'Meta_Fijada': r['Meta_Fijada'],
                    'Meta_Nacional': r['Meta_Nacional']
                })
        print(f"Reporte guardado en {output_path}")
    except Exception as e:
        print(f"Error escribiendo reporte: {e}")

if __name__ == "__main__":
    calcular_meta_7()
