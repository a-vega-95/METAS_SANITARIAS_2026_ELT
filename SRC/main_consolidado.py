import sys
import os
import csv
import openpyxl
import subprocess
from datetime import datetime

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'SRC'))

from modules.utils import normalize_path, load_center_names

from config import DATOS_DIR

def run_meta_scripts():
    """Ejecuta todos los scripts de cálculo de metas"""
    
    # Buscar archivo PIV más reciente y válido
    piv_dir = os.path.join(DATOS_DIR, "PIV")
    piv_files = [f for f in os.listdir(piv_dir) if f.startswith("PIV_") and f.endswith(".parquet")]
    if not piv_files:
        sys.exit(f"ERROR CRITICO: No se encontró ningún archivo PIV válido en: {piv_dir}. La ejecución no puede continuar.")
    # Selecciona el archivo más reciente por nombre
    piv_files.sort(reverse=True)
    piv_file = os.path.join(piv_dir, piv_files[0])
    print(f"Usando archivo PIV: {piv_file}")
    if not os.path.exists(piv_file):
        sys.exit(f"ERROR CRITICO: No se encontró el archivo PIV seleccionado en: {piv_file}. La ejecución no puede continuar.")
        
    scripts = [
        "SRC/metas/meta_1_dsm.py",
        "SRC/metas/meta_2_pap.py",
        "SRC/metas/meta_3_bucal.py",
        "SRC/metas/meta_4_dm2.py",
        "SRC/metas/meta_5_hta.py",
        "SRC/metas/meta_6_lactancia.py",
        "SRC/metas/meta_7_resp.py"
    ]
    
    print("=== Ejecutando Scripts de Metas ===")
    for script in scripts:
        script_path = normalize_path(script)
        if os.path.exists(script_path):
            print(f"Ejecutando {script}...")
            # Remove try/except to allow failure to stop execution as requested
            # "SI FALTA ALGUNO ESTE SE DETIENE"
            subprocess.run([sys.executable, script_path], check=True)
        else:
            print(f"Script no encontrado: {script_path}")
            # If a script is missing, should we stop too? Probably yes.
            sys.exit(f"Error Fatal: Script no encontrado {script_path}")
            
    print("=== Ejecución Finalizada ===")

def consolidar_reportes():
    # 1. Ejecutar Cálculos
    run_meta_scripts()
    
    print("\n=== Generando Reporte Consolidado de Rendimiento ===")
    
    map_nombres = load_center_names()
    
    output_dir = normalize_path("DATOS/RENDIMIENTO")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Buscar archivos de reporte preliminar de metas
    report_dir = normalize_path("DATOS")
    report_files = [f for f in os.listdir(report_dir) if f.startswith("reporte_meta_") and f.endswith("_preliminar.csv")]
    if not report_files:
        print("No se encontraron archivos de reporte preliminar de metas.")
        return

    consolidado = []

    for filename in report_files:
        csv_path = os.path.join(report_dir, filename)
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Leer datos del CSV (Source of Truth)
                        meta_id = row.get('Meta_ID', 'Desconocido')
                        indicador = row.get('Indicador', row.get('Nombre_Indicador', ''))
                        
                        try:
                            num = float(row.get('Numerador', 0))
                            den = float(row.get('Denominador', 0))
                            cump = float(row.get('Cumplimiento', row.get('Cumplimiento_Actual', 0)))
                            meta_fijada = float(row.get('Meta_Fijada', 0))
                            meta_nacional = float(row.get('Meta_Nacional', 0))
                        except ValueError:
                            continue

                        centro = row.get('Centro', 'Desconocido')
                        nombre_centro = map_nombres.get(centro, 'Desconocido')
                        if nombre_centro == 'Desconocido' and centro[-1].isalpha():
                             nombre_centro = map_nombres.get(centro[:-1], 'Desconocido')
                        
                        # Cálculos finales
                        brecha_fijada = meta_fijada - cump
                        brecha_nacional = meta_nacional - cump
                        
                        target_num = den * (meta_fijada / 100.0)
                        falta_para_meta = max(0, target_num - num)
                        
                        consolidado.append({
                            'Meta_ID': meta_id,
                            'Nombre_Indicador': indicador,
                            'COD_CENTRO': centro,
                            'Nombre_Centro': nombre_centro,
                            'Numerador_Actual': num,
                            'Denominador_Actual': den,
                            'Cumplimiento_Actual_%': round(cump, 2),
                            'Meta_Fijada_%': meta_fijada,
                            'Meta_Nacional_%': meta_nacional,
                            'Brecha_vs_Fijada_%': round(brecha_fijada, 2),
                            'Brecha_vs_Nacional_%': round(brecha_nacional, 2),
                            'Casos_Faltantes_Meta_Fijada': round(falta_para_meta, 0),
                            'Estado': 'Cumplido' if cump >= meta_fijada else 'Pendiente'
                        })
            except Exception as e:
                print(f"Error leyendo {csv_path}: {e}")
                
    if not consolidado:
        print("No se generaron datos para el reporte.")
    
    # Exportar Excel
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"Rendimiento_Metas_Sanitarias_{fecha_hoy}.xlsx"
    path_excel = os.path.join(output_dir, nombre_archivo)
    
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Consolidado"
        
        headers = ['Fecha_Corte', 'Meta_ID', 'Nombre_Indicador', 'COD_CENTRO', 'Nombre_Centro', 'Numerador_Actual', 'Denominador_Actual', 
                   'Cumplimiento_Actual_%', 'Meta_Fijada_%', 'Meta_Nacional_%', 'Brecha_vs_Fijada_%', 
                   'Brecha_vs_Nacional_%', 'Casos_Faltantes_Meta_Fijada', 'Estado']
        ws.append(headers)
        
        fecha_corte = datetime.now().strftime("%Y-%m-%d")
        
        for item in consolidado:
            item['Fecha_Corte'] = fecha_corte
            ws.append([item.get(h, '') for h in headers])
            
        print(f"Archivo generado: {path_excel}")
        wb.save(path_excel)
    except Exception as e:
        print(f"Error guardando Excel: {e}")

if __name__ == "__main__":
    consolidar_reportes()
