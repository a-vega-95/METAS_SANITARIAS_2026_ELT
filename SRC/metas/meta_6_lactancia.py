import sys
import os
import csv
import openpyxl

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'SRC'))

from modules.dataloaders import scan_rem_files, get_rem_value
from modules.utils import normalize_path

def calcular_meta_6():
    print("=== Calculando Meta 6: Lactancia Materna Exclusiva (LME) ===")
    
    # 1. Configuración
    DATA_DIR = r"DATOS\ENTRADA\SERIE_A"
    TARGET_SHEET = "A03"
    
    # Coordenadas
    # Numerador: H61 (LME)
    # Denominador: H61 + H62 + H63 (Total Controlados: LME + Mixta + Fórmula)
    # NOTA: H60 solía ser el total, pero la instrucción es sumar los componentes.
    COL = 'H'
    ROW_NUM = 61
    ROWS_DEN = [61, 62, 63]
    
    # 2. Escanear Archivos
    try:
        mapping = scan_rem_files(DATA_DIR)
        print(f"Se encontraron {len(mapping)} archivos REM en {DATA_DIR}.")
    except Exception as e:
        print(f"Error fatal escaneando archivos: {e}")
        return

    reporte = []
    
    # centros[code] = {'num': 0, 'den': 0}
    centros = {}
    
    for entry in mapping:
        code = entry['code']
        file_path = entry['path']
        year = entry['year']
        filename = entry['filename']
        
        if code not in centros:
            centros[code] = {'num': 0, 'den': 0}
            
        if not os.path.exists(file_path):
            continue
            
        # Lógica de Fechas
        # Numerador y Denominador para LME suelen evaluarse en el mismo periodo
        # Ojo: Logica dice "Denominador año anterior"?
        # VERIFICAR: Meta 6 user request: "Denominador: La sumatoria... en la columna del 6to mes".
        # En Logica de Negocio anterior decia "Denominador Año Anterior".
        # La instruccion RECIENTE del usuario dice "Se extrae del archivo REM A03...". No menciona año anterior explicitamente
        # PERO en la definicion de Meta 6 usual (COMGES) es corte transversal (mismo año) o longitud (cohortes).
        # El usuario dijo: "Meta 6: Lactancia Materna... Se extrae del archivo REM A03... Denominador: La sumatoria..."
        # Asumiremos MISMO PERIODO (2026) salvo que se mantenga la logica explicita de "Denominador Año Anterior" del plan previo.
        # Plan previo decia: "Meta 6 (LME): Denominador Año Anterior (2025)".
        # Voy a MANTENER la logica de Denominador 2025 si la meta es "Mantener LME de 2025 en 2026" o similar
        # O si es cohorte nacidos 2025 controlados 2026.
        # PERO la instruccion de celdas "H61" vs "H61+H62+H63" aplica a las celdas.
        # Mantendré la logica temporal (Num=2026, Den=2025) que ya estaba validada, solo cambiando las celdas.
        
        is_numerator_period = (year == 2026)
        is_denominator_period = (year == 2025)
        
        if not is_numerator_period and not is_denominator_period:
            continue
            
        num_local = 0
        den_local = 0
        
        try:
             wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
             if TARGET_SHEET in wb.sheetnames:
                 sheet = wb[TARGET_SHEET]
                 
                 # Numerator Period (2026)
                 if is_numerator_period:
                     val_num = sheet[f"{COL}{ROW_NUM}"].value
                     if val_num and isinstance(val_num, (int, float)):
                         num_local = val_num
                          
                 # Denominator Period (2025)
                 if is_denominator_period:
                     for r in ROWS_DEN:
                         val_den = sheet[f"{COL}{r}"].value
                         if val_den and isinstance(val_den, (int, float)):
                             den_local += val_den
                          
             wb.close()
        except Exception as e:
             print(f"Error reading {filename}: {e}")
             continue
            
        centros[code]['num'] += num_local
        centros[code]['den'] += den_local
        
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
            'Periodo': '2026 vs 2025',
            'Numerador': num,
            'Denominador': den,
            'Cumplimiento': cumplimiento
        })

    # 4. Resultado Final Global
    cumplimiento_global = (total_num / total_den * 100) if total_den > 0 else 0
    
    print("\n=== RESULTADOS GLOBALES META 6 ===")
    print(f"Numerador Total (LME): {total_num}")
    print(f"Denominador Total (Controlados): {total_den}")
    print(f"Cumplimiento Actual: {cumplimiento_global:.2f}%")
    print(f"Meta Fijada: 64.0%")
    
    # Guardar reporte
    output_path = normalize_path(r"DATOS\reporte_meta_6_preliminar.csv")
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Centro', 'Periodo', 'Numerador', 'Denominador', 'Cumplimiento'])
            writer.writeheader()
            writer.writerows(reporte)
        print(f"Reporte detallado guardado en: {output_path}")
    except Exception as e:
        print(f"Error escribiendo reporte: {e}")

if __name__ == "__main__":
    calcular_meta_6()
