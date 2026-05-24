"""
utils.py - Funciones auxiliares reutilizables para normalización de datasets
"""

import pandas as pd
import os
import sqlite3


def cargar_csv(ruta: str, encoding: str = "latin-1") -> pd.DataFrame:
    """Carga un archivo CSV con manejo de errores."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    df = pd.read_csv(ruta, encoding=encoding, dtype=str)
    print(f"[OK] Archivo cargado: {ruta} — {len(df):,} filas, {len(df.columns)} columnas")
    return df


def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia espacios en blanco y normaliza strings."""
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df


def exportar_csv(df: pd.DataFrame, ruta: str, nombre: str) -> None:
    """Exporta un DataFrame a CSV."""
    os.makedirs(ruta, exist_ok=True)
    filepath = os.path.join(ruta, f"{nombre}.csv")
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"[CSV] Exportado: {filepath} — {len(df):,} filas")


def exportar_sqlite(tablas: dict, db_path: str) -> None:
    """
    Exporta un diccionario {nombre_tabla: DataFrame} a una base de datos SQLite.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    for nombre, df in tablas.items():
        df.to_sql(nombre, conn, if_exists="replace", index=False)
        print(f"[SQLite] Tabla '{nombre}' cargada — {len(df):,} filas")
    conn.close()
    print(f"[SQLite] Base de datos guardada en: {db_path}")


def generar_id_secuencial(df: pd.DataFrame, columna_origen: str, prefix: str = "") -> pd.Series:
    """
    Dado un DataFrame con valores únicos en columna_origen,
    devuelve una Serie con IDs enteros consecutivos mapeados.
    """
    valores_unicos = df[columna_origen].drop_duplicates().reset_index(drop=True)
    mapeo = {v: i + 1 for i, v in enumerate(valores_unicos)}
    return df[columna_origen].map(mapeo)


def reporte_redundancia(df_original: pd.DataFrame, tablas_normalizadas: dict) -> None:
    """Imprime un resumen comparativo antes y después de normalizar."""
    celdas_original = df_original.shape[0] * df_original.shape[1]
    celdas_norm = sum(t.shape[0] * t.shape[1] for t in tablas_normalizadas.values())
    reduccion = (1 - celdas_norm / celdas_original) * 100

    print("\n===== REPORTE DE NORMALIZACIÓN =====")
    print(f"Filas originales  : {df_original.shape[0]:>10,}")
    print(f"Columnas originales: {df_original.shape[1]:>9}")
    print(f"Celdas originales : {celdas_original:>10,}")
    print()
    for nombre, t in tablas_normalizadas.items():
        print(f"  Tabla '{nombre}': {len(t):,} filas × {len(t.columns)} cols")
    print(f"\nCeldas normalizadas: {celdas_norm:>9,}")
    print(f"Reducción estimada: {reduccion:>9.1f}%")
    print("====================================\n")
