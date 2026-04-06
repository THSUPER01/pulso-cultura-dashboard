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


def generate_aggregates(data):
    """Generate aggregated statistics from records (no PII, no individual records)."""
    records = data["records"]
    questions = data["questions"]
    filter_options = data["filterOptions"]

    aggregates = {
        "totalRecords": len(records),
        "favorabilidadPorPregunta": {},
        "favorabilidadPorDimension": {},
        "favorabilidadPorVariable": {},
        "favorabilidadPorCentro": {},
        "favorabilidadPorPlanta": {},
        "favorabilidadPorGenero": {},
        "favorabilidadPorEdad": {},
        "favorabilidadPorAntiguedad": {},
        "favorabilidadPorEstudios": {},
    }

    def calc_favorabilidad(values_list):
        total = len(values_list)
        if total == 0:
            return {"favorable": 0, "indeciso": 0, "desfavorable": 0}
        favorable = sum(1 for v in values_list if v == 1)
        indeciso = sum(1 for v in values_list if v == 0)
        desfavorable = sum(1 for v in values_list if v == -1)
        return {
            "favorable": round(favorable / total * 100, 1),
            "indeciso": round(indeciso / total * 100, 1),
            "desfavorable": round(desfavorable / total * 100, 1),
        }

    for i, q in enumerate(questions):
        q_key = f"q{i}"
        values = [r.get(q_key, 0) for r in records]
        aggregates["favorabilidadPorPregunta"][q["text"]] = {
            **calc_favorabilidad(values),
            "dimension": q["dimension"],
            "variable": q["variable"],
        }

    dimensions = {}
    for q in questions:
        dim = q["dimension"]
        if dim not in dimensions:
            dimensions[dim] = []
        q_key = f"q{questions.index(q)}"
        dimensions[dim].extend([r.get(q_key, 0) for r in records])

    for dim, values in dimensions.items():
        aggregates["favorabilidadPorDimension"][dim] = calc_favorabilidad(values)

    variables = {}
    for q in questions:
        var = q["variable"]
        if var not in variables:
            variables[var] = []
        q_key = f"q{questions.index(q)}"
        variables[var].extend([r.get(q_key, 0) for r in records])

    for var, values in variables.items():
        aggregates["favorabilidadPorVariable"][var] = calc_favorabilidad(values)

    centros = {}
    for r in records:
        centro = r.get("centro", "N/A")
        if centro not in centros:
            centros[centro] = []
        for i in range(len(questions)):
            centros[centro].append(r.get(f"q{i}", 0))

    for centro, values in centros.items():
        aggregates["favorabilidadPorCentro"][centro] = calc_favorabilidad(values)

    plantas = {}
    for r in records:
        planta = r.get("planta", "N/A")
        if planta not in plantas:
            plantas[planta] = []
        for i in range(len(questions)):
            plantas[planta].append(r.get(f"q{i}", 0))

    for planta, values in plantas.items():
        aggregates["favorabilidadPorPlanta"][planta] = calc_favorabilidad(values)

    generos = {}
    for r in records:
        genero = r.get("genero", "N/A")
        if genero not in generos:
            generos[genero] = []
        for i in range(len(questions)):
            generos[genero].append(r.get(f"q{i}", 0))

    for genero, values in generos.items():
        aggregates["favorabilidadPorGenero"][genero] = calc_favorabilidad(values)

    edades = {}
    for r in records:
        edad = r.get("edad", "N/A")
        if edad not in edades:
            edades[edad] = []
        for i in range(len(questions)):
            edades[edad].append(r.get(f"q{i}", 0))

    for edad, values in edades.items():
        aggregates["favorabilidadPorEdad"][edad] = calc_favorabilidad(values)

    antiguedades = {}
    for r in records:
        antiguedad = r.get("antiguedad", "N/A")
        if antiguedad not in antiguedades:
            antiguedades[antiguedad] = []
        for i in range(len(questions)):
            antiguedades[antiguedad].append(r.get(f"q{i}", 0))

    for antiguedad, values in antiguedades.items():
        aggregates["favorabilidadPorAntiguedad"][antiguedad] = calc_favorabilidad(values)

    estudios_dict = {}
    for r in records:
        estudios = r.get("estudios", "N/A")
        if estudios not in estudios_dict:
            estudios_dict[estudios] = []
        for i in range(len(questions)):
            estudios_dict[estudios].append(r.get(f"q{i}", 0))

    for estudios, values in estudios_dict.items():
        aggregates["favorabilidadPorEstudios"][estudios] = calc_favorabilidad(values)

    return aggregates


def save_dashboard_data_for_api(data):
    """Save aggregated data + metadata for Netlify API function."""
    aggregates = generate_aggregates(data)

    api_data = {
        "questions": data["questions"],
        "filterOptions": data["filterOptions"],
        "aggregates": aggregates,
        "timestamp": pd.Timestamp.now().isoformat(),
    }

    cache_dir = os.path.join(BASE_DIR, "functions", "cache")
    os.makedirs(cache_dir, exist_ok=True)

    cache_file = os.path.join(cache_dir, "dashboard_data.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)

    print(f"API data saved: {cache_file}")
    return api_data


def render_dashboard(data_for_template):
    """Render Jinja2 template with metadata (NO individual records)."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,
    )
    template = env.get_template("dashboard.html.j2")

    data_json = json.dumps(data_for_template, ensure_ascii=False, separators=(",", ":"))

    html = template.render(dashboard_data_json=data_json)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard generated: {OUTPUT_FILE}")
    print(f"Template includes: Questions metadata + Filter options (NO raw records)")


def main():
    xlsx_path = find_xlsx()
    print(f"Reading: {xlsx_path}")
    data = read_and_process(xlsx_path)

    # Save aggregated data for API (includes records for aggregation only)
    api_data = save_dashboard_data_for_api(data)

    # Prepare template data: metadata only (NO individual records)
    template_data = {
        "questions": data["questions"],
        "filterOptions": data["filterOptions"],
    }

    # Render dashboard template
    render_dashboard(template_data)
    print(f"Total records processed: {len(data['records'])}")


if __name__ == "__main__":
    main()
