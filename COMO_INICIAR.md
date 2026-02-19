# Guía de Inicio Rápido: Metas Sanitarias 2026

Bienvenido al sistema de evaluación de Metas Sanitarias 2026. Esta guía te orientará sobre cómo obtener y cargar los datos necesarios para ejecutar el sistema.

## 1. Obtención de Datos

Para que el sistema funcione, necesitas dos fuentes de información críticas: Archivos REM y Archivos PIV.

### A. Archivos REM (Registro Estadístico Mensual)
Son registros públicos de atenciones de salud.

- **Fuente Oficial**: [Departamento de Estadísticas Araucanía Sur](https://estadistica.araucaniasur.cl/?page_id=9837)
- **Qué descargar**:
  - Debes navegar por el sitio y descargar los archivos Excel correspondientes a tu comuna/centro para el año en curso y el año anterior.
  - Se requieren archivos de **Serie A** (Controles, Actividades) y **Serie P** (Población bajo control).

### B. Archivos PIV (Población Inscrita Validada)
Es el maestro de usuarios inscritos validado por FONASA.

- **Fuente**: FONASA / Gestión Propia.
- **Cómo obtenerlo**: Este archivo no es público. Debe ser solicitado o generado por el encargado de estadística o per cápita de su Departamento de Salud Municipal (DESAM) o CESFAM.
- **Formato ideal**: `.parquet` (para mayor velocidad) o `.csv`. El sistema espera un archivo maestro con columnas como `COD_CENTRO`, `EDAD_EN_FECHA_CORTE`, `GENERO`, etc.

## 2. Preparación de Carpetas

Una vez tengas los archivos, debes organizarlos en la carpeta `DATOS/ENTRADA` siguiendo esta estructura lógica:

### Para datos del Año Actual (ej: 2026)
Ubicación: `DATOS/ENTRADA/REM_ANO_ACTUAL/`

- **Serie A**: Copia las carpetas mensuales (ej: `ENE_2026`, `FEB_2026`) dentro de `DATOS/ENTRADA/REM_ANO_ACTUAL/SERIE_A/`.
- **Serie P**: Copia los archivos Excel de población (ej: `121305P.xlsm`) dentro de `DATOS/ENTRADA/REM_ANO_ACTUAL/SERIE_P/`.

### Para datos del Año Pasado (ej: 2025)
Algunas metas (como la Meta 1) requieren comparar con el año anterior.

Ubicación: `DATOS/ENTRADA/REM_ANO_PASADO/`

- **Serie A**: Copia las carpetas de los meses requeridos (ej: `OCT_2025`, `NOV_2025`, `DIC_2025`) dentro de `DATOS/ENTRADA/REM_ANO_PASADO/SERIE_A/`.

### Archivo Maestro PIV
- Coloca tu archivo PIV único en la carpeta `DATOS/PIV/`.

## 3. Ejecución

1.  Abre una terminal en la carpeta principal del proyecto.
2.  Ejecuta el comando:
    ```bash
    python SRC/main_consolidado.py
    ```
3.  El sistema procesará los datos y generará un reporte Excel en `DATOS/RENDIMIENTO/`.

## Notas Importantes
- **No cambies los nombres de las carpetas principales** (`REM_ANO_ACTUAL`, `REM_ANO_PASADO`), ya que el sistema las busca automáticamente.
- Si descargas nuevos archivos REM mes a mes, simplemente agrégalos a las carpetas correspondientes y vuelve a ejecutar el script.
