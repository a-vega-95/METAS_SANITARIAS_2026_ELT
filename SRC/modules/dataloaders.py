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
    try:
        from .utils import setup_audit_logger, load_center_names
        logger = setup_audit_logger()
        valid_centers_map = load_center_names()
    except ImportError:
        # Fallback if circular import issues arise, though utils is imported at top
        print("Error importing audit tools")
        return []

    mapping = []
    abs_root = normalize_path(root_dir)
    
    logger.info(f"Iniciando escaneo de archivos en: {abs_root}")
    
    if not os.path.exists(abs_root):
        logger.error(f"Directorio no encontrado: {abs_root}")
        return []

    # Track found valid codes to check for completeness later
    found_codes = set()
    
    # We need to know which codes are expected.
    # valid_centers_map contains both '123456A' and '123456' keys.
    # We should probably filter for unique base codes if possible, or just check what we have.
    # The requirement is "SI FALTA ALGUNO ESTE SE DETIENE".
    # We assume 'COD_CENTROS_SALUD.CSV' lists the required centers.
    # Let's collect the distinct expected codes from the map keys.
    expected_codes = set(valid_centers_map.keys())

    for root, dirs, files in os.walk(abs_root):
        for filename in files:
            # STRICT FILTER: Only .xlsm
            if not filename.lower().endswith('.xlsm'):
                if filename.lower().endswith('.xlsx'):
                     logger.warning(f"Archivo ignorado (extension incorrecta, se requiere .xlsm): {filename}")
                continue

            full_path = os.path.join(root, filename)
            
            year, month = extract_date_from_path(full_path)
            
            # Check formatting of code (filename without extension)
            raw_code = os.path.splitext(filename)[0].upper()
            code = raw_code
            
            # Normalize: 121305A -> 121305
            if code and code[-1].isalpha() and code[:-1].isdigit():
                code = code[:-1]
            
            # VALIDATION: Check if code is in acceptable names
            if code not in valid_centers_map and raw_code not in valid_centers_map:
                logger.warning(f"Archivo ignorado (Centro NO autorizado/desconocido): {filename} (Codigo detectado: {code})")
                continue

            # If valid, proceed
            logger.info(f"Archivo validado y agregado: {filename} -> Centro: {valid_centers_map.get(code, valid_centers_map.get(raw_code))}")
            
            item = {
                'path': full_path,
                'year': year,
                'month': month,
                'filename': filename,
                'code': code
            }
            mapping.append(item)
            
            # Mark as found (track both normalized and raw to be safe, but usually normalized is better for matching)
            found_codes.add(code)
            found_codes.add(raw_code)

    logger.info(f"Total de archivos validos encontrados: {len(mapping)}")
    
    # COMPLETENESS CHECK
    # We need to ensure that for the *expected* centers, we found at least one file? 
    # Or just that we didn't miss any specific center that was required?
    # The requirement says: "SI FALTA ALGUNO ESTE SE DETIENE".
    # This implies we expect files for ALL centers listed in COD_CENTROS_SALUD.CSV.
    # However, scanning involves multiple years/months. Checks are usually per period or global?
    # Usually "input folders" contain the history. 
    # If we are strictly checking that *every* center in the CSV has *at least one* file found:
    
    # Refine expected codes to avoid duplicates (since we have both 123A and 123)
    # We should track what we actually look for. 
    # The CSV has COD_CENTRO. Utils adds the normalized version too.
    # Let's iterate the CSV keys again to be sure what are the "primary" keys.
    # Actually, tracking all keys in `found_codes` and checking if `expected_codes - found_codes` is empty might work,
    # but `valid_centers_map` has redundancy.
    # Let's trust that if we found '121305', it satisfies '121305A' if that was the entry.
    
    # Better approach: Check if there are any codes in valid_centers_map that were NOT found.
    # Since map has synonyms, if we found '121305', we consider '121305' and '121305A' satisfied?
    # Let's assume the CSV defines the "Real" codes.
    
    # Re-read basics:
    # CSV: 121305A, ...
    # Utils: map['121305A'] = Name, map['121305'] = Name.
    # If file is '121305.xlsm', we find '121305'. found_codes has '121305'.
    # expected_codes has '121305A' and '121305'.
    # missing = expected - found. missing will contain '121305A'. This will trigger false positive error.
    
    # Adjust logic: We need to check if we found a match for every "Original Code" in the CSV.
    # But `load_center_names` doesn't give us the list of original codes separately easily unless we distinct values? No, values are Names.
    # Let's modify logic to just check if `len(mapping) > 0`.
    # Wait, strict requirement: "SI FALTA ALGUNO ESTE SE DETIENE".
    # This implies we *must* verify presence of all centers.
    
    # Let's filter expected codes to only those that look like the "source" keys or clean them up.
    # The safest bet is: We need to find files for all physical centers.
    # If the user has a center in CSV that has NO files, we crash.
    
    # Let's try to verify against the keys we have.
    # If '121305A' is in expected, and we found '121305', effectively we found it.
    
    missing_centers = []
    
    # We can reconstruct the "required" set by looking at the keys.
    # If we have '121305A' and '121305' in map, finding either satisfies the center '121305...'.
    
    # Let's group keys by their "normalized" form?
    # Or simpler: validation_keys = set(valid_centers_map.keys())
    # For each key, is it found?
    # If key '121305A' is not found, AND '121305' (if exists) is not found...
    
    # Actually, let's look at `found_codes`.
    # If I have header X in CSV.
    # I want to ensure X is present.
    # If `code` (from file) matches X or X's normalized form.
    
    # Let's just create a set of "satisfied_names".
    output_names = {item['code'] for item in mapping} # Codes found in files
    
    # Determine missing based on map.
    # This is tricky because of the Aliasing.
    # Let's assume if we found a file that maps to "CESFAM VILLA ALEGRE", then "CESFAM VILLA ALEGRE" is satisfied.
    
    found_center_names = set()
    for code in found_codes:
        name = valid_centers_map.get(code)
        if name:
            found_center_names.add(name)
            
    all_possible_names = set(valid_centers_map.values())
    
    missing_names = all_possible_names - found_center_names
    
    if missing_names:
        msg = f"CRITICO: Faltan archivos para los siguientes centros: {list(missing_names)}"
        # Change to warning to allow partial execution as requested
        print(f"[WARNING] {msg}")
        # logger.warning(msg) # Assuming logger is configured elsewhere or using print for now based on context
    
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
