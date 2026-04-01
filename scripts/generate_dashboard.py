#!/usr/bin/env python3
"""
generate_dashboard.py
Reads the first .xlsx in data/, processes survey data,
and renders a self-contained dashboard HTML via Jinja2.
"""

import json
import os
import glob
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATE_DIR = os.path.join(BASE_DIR, "scripts", "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "docs")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dashboard.html")

# Column mapping (0-indexed after pandas read)
COL_MAP = {
    "id": 0,        # A
    "genero": 1,     # B
    "edad": 2,       # C
    "antiguedad": 3, # D
    "estudios": 4,   # E
    "centro": 5,     # F - Lugar de trabajo
    "planta": 6,     # G
}

# Question columns H-U (indices 7-20)
QUESTION_COLS = list(range(7, 21))

# Question -> Variable -> Dimension mapping
QUESTION_MAPPING = [
    {
        "col_index": 7,
        "variable": "Cuidado",
        "dimension": "Respeto",
    },
    {
        "col_index": 8,
        "variable": "Ausencia de favoritismo",
        "dimension": "Imparcialidad",
    },
    {
        "col_index": 9,
        "variable": "Equidad en la remuneraci\u00f3n y trato",
        "dimension": "Imparcialidad",
    },
    {
        "col_index": 10,
        "variable": "Desarrollo y reconocimiento",
        "dimension": "Respeto",
    },
    {
        "col_index": 11,
        "variable": "Fraternidad",
        "dimension": "Compa\u00f1erismo",
    },
    {
        "col_index": 12,
        "variable": "Equidad en la remuneraci\u00f3n y trato",
        "dimension": "Imparcialidad",
    },
    {
        "col_index": 13,
        "variable": "Participaci\u00f3n",
        "dimension": "Respeto",
    },
    {
        "col_index": 14,
        "variable": "Participaci\u00f3n",
        "dimension": "Respeto",
    },
    {
        "col_index": 15,
        "variable": "Ausencia de favoritismo",
        "dimension": "Imparcialidad",
    },
    {
        "col_index": 16,
        "variable": "Comunicaci\u00f3n",
        "dimension": "Credibilidad",
    },
    {
        "col_index": 17,
        "variable": "Comunicaci\u00f3n",
        "dimension": "Credibilidad",
    },
    {
        "col_index": 18,
        "variable": "Cuidado",
        "dimension": "Respeto",
    },
    {
        "col_index": 19,
        "variable": "Preguntas Abierta",
        "dimension": "Preguntas Abierta",
    },
    {
        "col_index": 20,
        "variable": "Preguntas Abierta",
        "dimension": "Preguntas Abierta",
    },
]

# Ordered filter options
EDAD_ORDER = [
    "Menor de 23 a\u00f1os",
    "Entre 23 a\u00f1os y menos de 30",
    "Entre 30 a\u00f1os y menos de 39",
    "Entre 39 a\u00f1os y menos de 52",
    "52 a\u00f1os o m\u00e1s",
]

ESTUDIOS_ORDER = [
    "Bachiller- secundaria",
    "Una carrera t\u00e9cnica",
    "Una carrera tecnol\u00f3gica",
    "Una carrera con titulo profesional",
    "Un posgrado (especializaci\u00f3n, maestr\u00eda o doctorado)",
    "Otros estudios",
]

ANTIGUEDAD_ORDER = [
    "Entre 0 a 3 meses",
    "M\u00e1s de 3 meses",
]


def find_xlsx():
    """Find first .xlsx file in data directory."""
    pattern = os.path.join(DATA_DIR, "*.xlsx")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No .xlsx files found in {DATA_DIR}")
    return files[0]


def normalize_antiguedad(val):
    """Group antiguedad: 'Entre 0 a 3 meses' stays, everything else -> 'Más de 3 meses'."""
    if not val or pd.isna(val):
        return "M\u00e1s de 3 meses"
    val_clean = str(val).strip()
    if "0 a 3" in val_clean or "0 a 3" in val_clean.lower():
        return "Entre 0 a 3 meses"
    return "M\u00e1s de 3 meses"


def read_and_process(filepath):
    """Read Excel and return processed data structure."""
    df = pd.read_excel(filepath, sheet_name=0, header=0)

    # Clean column names (strip whitespace)
    df.columns = [str(c).strip() for c in df.columns]

    # Get original headers for questions
    all_headers = list(df.columns)

    records = []
    questions = []

    # Build question metadata
    for i, mapping in enumerate(QUESTION_MAPPING):
        col_idx = mapping["col_index"]
        header = all_headers[col_idx] if col_idx < len(all_headers) else f"Pregunta {i+1}"
        questions.append({
            "key": f"q{i}",
            "text": header,
            "variable": mapping["variable"],
            "dimension": mapping["dimension"],
        })

    # Process records
    for _, row in df.iterrows():
        record = {}

        # Demographics
        record["id"] = int(row.iloc[COL_MAP["id"]]) if pd.notna(row.iloc[COL_MAP["id"]]) else 0
        record["genero"] = str(row.iloc[COL_MAP["genero"]]).strip() if pd.notna(row.iloc[COL_MAP["genero"]]) else ""
        record["edad"] = str(row.iloc[COL_MAP["edad"]]).strip() if pd.notna(row.iloc[COL_MAP["edad"]]) else ""
        record["estudios"] = str(row.iloc[COL_MAP["estudios"]]).strip() if pd.notna(row.iloc[COL_MAP["estudios"]]) else ""
        record["centro"] = str(row.iloc[COL_MAP["centro"]]).strip() if pd.notna(row.iloc[COL_MAP["centro"]]) else ""
        record["planta"] = str(row.iloc[COL_MAP["planta"]]).strip() if pd.notna(row.iloc[COL_MAP["planta"]]) else ""

        # Normalize antiguedad
        raw_ant = row.iloc[COL_MAP["antiguedad"]] if pd.notna(row.iloc[COL_MAP["antiguedad"]]) else ""
        record["antiguedad"] = normalize_antiguedad(raw_ant)

        # Question responses (coerce to int, default 0)
        for i, mapping in enumerate(QUESTION_MAPPING):
            col_idx = mapping["col_index"]
            val = row.iloc[col_idx] if col_idx < len(row) else None
            try:
                record[f"q{i}"] = int(float(val)) if pd.notna(val) else 0
            except (ValueError, TypeError):
                record[f"q{i}"] = 0

        records.append(record)

    # Build filter options
    genero_vals = sorted(df.iloc[:, COL_MAP["genero"]].dropna().astype(str).str.strip().unique().tolist())
    centro_vals = sorted(df.iloc[:, COL_MAP["centro"]].dropna().astype(str).str.strip().unique().tolist())
    planta_vals = sorted(df.iloc[:, COL_MAP["planta"]].dropna().astype(str).str.strip().unique().tolist())

    # Use predefined orders for edad, estudios, antiguedad
    filter_options = {
        "genero": genero_vals,
        "edad": EDAD_ORDER,
        "antiguedad": ANTIGUEDAD_ORDER,
        "estudios": ESTUDIOS_ORDER,
        "centro": centro_vals,
        "planta": planta_vals,
    }

    return {
        "records": records,
        "questions": questions,
        "filterOptions": filter_options,
    }


def render_dashboard(data):
    """Render Jinja2 template with embedded data."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
    )
    template = env.get_template("dashboard.html.j2")

    # Convert data to JSON string for embedding
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    html = template.render(dashboard_data_json=data_json)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard generated: {OUTPUT_FILE}")
    print(f"Records: {len(data['records'])}, Questions: {len(data['questions'])}")


def main():
    xlsx_path = find_xlsx()
    print(f"Reading: {xlsx_path}")
    data = read_and_process(xlsx_path)
    render_dashboard(data)


if __name__ == "__main__":
    main()
