import os
import csv
import openpyxl
import pyarrow.parquet as pq
from .utils import normalize_path

def extract_date_from_path(file_path):
    """
    Extracts year and month from a file path.
    Returns (year, month_int) or (None, None).
    Month is 1-12.
    """
    path_parts = normalize_path(file_path).split(os.sep)
    
    year = None
    month = None
    
    # Grid of month names to int
    MONTH_MAP = {
        'ENE': 1, 'JAN': 1, 'ENERO': 1, 'JANUARY': 1,
        'FEB': 2, 'FEBRERO': 2, 'FEBRUARY': 2,
        'MAR': 3, 'MARZO': 3, 'MARCH': 3,
        'ABR': 4, 'APR': 4, 'ABRIL': 4, 'APRIL': 4,
        'MAY': 5, 'MAYO': 5,
        'JUN': 6, 'JUNIO': 6, 'JUNE': 6,
        'JUL': 7, 'JULIO': 7, 'JULY': 7,
        'AGO': 8, 'AUG': 8, 'AGOSTO': 8, 'AUGUST': 8,
        'SEP': 9, 'SEPT': 9, 'SEPTIEMBRE': 9, 'SEPTEMBER': 9,
        'OCT': 10, 'OCTUBRE': 10, 'OCTOBER': 10,
        'NOV': 11, 'NOVIEMBRE': 11, 'NOVEMBER': 11,
        'DIC': 12, 'DEC': 12, 'DICIEMBRE': 12, 'DECEMBER': 12
    }
    
    for part in path_parts:
        part_upper = part.upper()
        
        # Check for Year (4 digits)
        if part.isdigit() and len(part) == 4 and part.startswith('20'):
            year = int(part)
            
        # Check for Month (in Month Map)
        # Sometimes month is like "OCT_2025" or "01_ENERO"
        # We split by _ or - or space
        subparts = part_upper.replace('_', ' ').replace('-', ' ').split()
        for sub in subparts:
            if sub in MONTH_MAP:
                month = MONTH_MAP[sub]
                
    return year, month

def scan_rem_files(root_dir):
    """
    Scans a directory for Excel files and extracts metadata.
    Returns list of dicts:
    [{'path': ..., 'year': ..., 'month': ..., 'filename': ..., 'code': ...}]
    """
    mapping = []
    abs_root = normalize_path(root_dir)
    
    if not os.path.exists(abs_root):
        print(f"Directory not found: {abs_root}")
        return []
        
    for root, dirs, files in os.walk(abs_root):
        for filename in files:
            if filename.lower().endswith(('.xlsx', '.xlsm')):
                full_path = os.path.join(root, filename)
                
                year, month = extract_date_from_path(full_path)
                
                # Check formatting of code (filename without extension)
                code = os.path.splitext(filename)[0].upper()
                
                # Normalize: 121305A -> 121305
                # This ensures consistent matching with PIV.
                if code and code[-1].isalpha() and code[:-1].isdigit():
                    code = code[:-1]
                
                mapping.append({
                    'path': full_path,
                    'year': year,
                    'month': month,
                    'filename': filename,
                    'code': code
                })
                
    return mapping

def get_rem_value(file_path, sheet_name, cell_coordinate):
    """
    Opens an Excel file and retrieves a value from a specific sheet and cell.
    Returns 0 if cell is empty or invalid.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return 0
        
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
        if sheet_name not in wb.sheetnames:
            print(f"Sheet {sheet_name} not found in {file_path}")
            wb.close()
            return 0
            
        sheet = wb[sheet_name]
        val = sheet[cell_coordinate].value
        wb.close()
        
        if val and isinstance(val, (int, float)):
            return val
        return 0
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def load_piv_data(parquet_path):
    """
    Loads the PIV Master Parquet file into a list of dictionaries using PyArrow.
    """
    abs_path = normalize_path(parquet_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"PIV file not found: {abs_path}")
    
    table = pq.read_table(abs_path, columns=['COD_CENTRO', 'EDAD_EN_FECHA_CORTE', 'ACEPTADO_RECHAZADO', 'GENERO', 'GENERO_NORMALIZADO'])
    # Convert to list of dicts for easier consumption without pandas
    return table.to_pylist()
