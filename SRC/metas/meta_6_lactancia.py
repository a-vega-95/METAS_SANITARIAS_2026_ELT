import sys
import os
import csv
import openpyxl

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'SRC'))

from modules.dataloaders import scan_rem_files
from modules.utils import normalize_path
from config import DIR_SERIE_A_ACTUAL, AGNO_ACTUAL

def calcular_meta_6():
    print("=== Calculando Meta 6: Lactancia Materna Exclusiva (LME) ===")
    
    # Configuración
    # LME: Numerador y Denominador del mismo año calendario (Ene-Dic 2026)
    
    COL = 'H'
    ROW_NUM = 61 # LME al 6to mes
    ROWS_DEN = [61, 62, 63] # LME + Fórmula + Mixta
    
    mapping = scan_rem_files(DIR_SERIE_A_ACTUAL)

    numeradores = {}
    denominadores = {}
    
    for entry in mapping:
        code = entry['code'] # Already normalized
        file_path = entry['path']
        year = entry['year']
        
        # Filtro Año: Todo 2026
        if year != AGNO_ACTUAL: continue
        
        if code not in numeradores:
            numeradores[code] = 0
            denominadores[code] = 0
            
        if not os.path.exists(file_path): continue
        
        try:
             wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
             if "A03" in wb.sheetnames:
                 sheet = wb["A03"]
                 
                 # Numerador
                 val_num = sheet[f"{COL}{ROW_NUM}"].value
                 if val_num and isinstance(val_num, (int, float)):
                     numeradores[code] += val_num
                     
                 # Denominador
                 den_local = 0
                 for r in ROWS_DEN:
                     val = sheet[f"{COL}{r}"].value
                     if val and isinstance(val, (int, float)):
                         den_local += val
                 denominadores[code] += den_local
                 
             wb.close()
        except: pass
        
    # Reporte
    reporte = []
    all_centers = set(numeradores.keys()) | set(denominadores.keys())
    
    for c in all_centers:
        num = numeradores.get(c, 0)
        den = denominadores.get(c, 0)
        cump = (num/den*100) if den > 0 else 0
        
        reporte.append({
            'Centro': c, 'Meta_ID': 'Meta 6', 'Indicador': 'LME 6to Mes',
            'Numerador': num, 'Denominador': den, 'Cumplimiento': cump,
            'Meta_Fijada': 64.0, 'Meta_Nacional': 60.0
        })
        
    output_path = normalize_path(r"DATOS\reporte_meta_6_preliminar.csv")
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Centro', 'Meta_ID', 'Indicador', 'Numerador', 'Denominador', 'Cumplimiento', 'Meta_Fijada', 'Meta_Nacional'])
            writer.writeheader()
            for r in reporte:
                writer.writerow(r)
        print(f"Reporte guardado en {output_path}")
    except: pass

if __name__ == "__main__":
    calcular_meta_6()
