# Proyecto de Evaluación Metas Sanitarias 2026 (Ley 19.813)

Este repositorio contiene el sistema automatizado ELT (Extract, Load, Transform) para el cálculo y monitoreo del cumplimiento de las Metas Sanitarias de Atención Primaria de Salud para el año 2026, desarrollado en conformidad con la normativa vigente (Resolución Exenta N° 650).

## Objetivo General
Automatizar el procesamiento de datos estadísticos (REM y PIV) para calcular indicadores de desempeño sanitario, minimizando el error humano y acelerando la generación de reportes de cumplimiento para la gestión municipal.

## Indicadores Evaluados (Metas)

El sistema cubre el cálculo de las 7 metas principales:

1.  **Meta 1**: Recuperación del Desarrollo Psicomotor.
2.  **Meta 2**: Cobertura de Papanicolaou (PAP) en mujeres de 25 a 64 años.
3.  **Meta 3**: Alta Odontológica (CERO y Libre de Caries).
4.  **Meta 4**: Compensación de Diabetes Mellitus Tipo 2 y Evaluación de Pie Diabético.
5.  **Meta 5**: Cobertura Efectiva de Hipertensión Arterial (HTA).
    - *Características*: Implementa prevalencia estratificada por grupos etarios según Res. 650.
6.  **Meta 6**: Lactancia Materna Exclusiva (LME).
    - *Características*: Cálculo corregido sin desfase temporal (año calendario actual).
7.  **Meta 7**: Cobertura de Enfermedades Respiratorias (Asma y EPOC).
    - *Características*: Utiliza REM P3 y prevalencias nacionales aditivas (Asma 10% + EPOC 11.7%).

## Cómo Empezar

Si eres nuevo utilizando este sistema, lee primero nuestra guía de inicio para saber cómo cargar los datos correctamente:

**[LEER GUÍA: CÓMO INICIAR Y CARGAR DATOS](COMO_INICIAR.md)**

Esta guía te explicará dónde descargar los REM oficiales (SSAS Sur) y cómo gestionar los archivos PIV de FONASA.

## Tecnologías y Estructura

- **Lenguaje**: Python 3.10+
- **Librerías Clave**: `pandas` (procesamiento), `openpyxl` (lectura Excel), `pyarrow` (lectura Parquet).
- **Arquitectura**:
  - `SRC/`: Código fuente.
    - `main_consolidado.py`: Script principal orquestador.
    - `config.py`: Configuración centralizada de variables.
    - `metas/`: Lógica específica para cada indicador.
  - `DATOS/`: Almacenamiento de insumos y salidas.

## Ejecución del Sistema

Una vez cargados los datos según la guía `COMO_INICIAR.md`:

```bash
# Ejecutar el consolidador principal
python SRC/main_consolidado.py
```

El resultado será un archivo Excel en `DATOS/RENDIMIENTO/` con el estado de cumplimiento de cada centro, brechas y porcentajes actualizados, listo para ser analizado o conectado a herramientas de BI (Power BI, Tableau).

---
*Desarrollado para la gestión eficiente de la Salud Pública.*