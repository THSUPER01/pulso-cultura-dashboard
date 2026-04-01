# Pulso Cultura - Dashboard Dinamico

Dashboard interactivo estilo Tableau para visualizar los resultados de la encuesta **Pulso Cultura** de Super de Alimentos S.A.

- Filtros en tiempo real (genero, edad, antiguedad, estudios, centro, planta)
- Graficas de favorabilidad por pregunta, centro, planta, dimension y variable
- Tabla detallada dimension / variable / pregunta
- Exportar datos filtrados a CSV
- Un solo archivo HTML self-contained (funciona offline)

---

## Inicio rapido

### 1. Clonar el repositorio

```bash
gh repo clone THSUPER01/pulso-cultura-dashboard
cd pulso-cultura-dashboard
```

### 2. Colocar tu archivo Excel

Reemplaza el archivo en `data/` con tu propio `.xlsx` (misma estructura de columnas):

```
data/
  Mi encuesta.xlsx
```

### 3. Generar el dashboard localmente

```bash
pip install pandas openpyxl jinja2
python scripts/generate_dashboard.py
```

Esto genera `docs/dashboard.html`. Abrelo directamente en el navegador.

---

## Despliegue con GitHub Pages

### Configurar Pages

1. Ve a **Settings** > **Pages** en tu repositorio
2. Source: **Deploy from a branch**
3. Branch: `main` / Folder: `/docs`
4. Guarda

El dashboard estara disponible en `https://THSUPER01.github.io/pulso-cultura-dashboard/dashboard.html`

### Despliegue automatico

El workflow de GitHub Actions se ejecuta automaticamente cuando:
- Se hace push a `main` con cambios en `data/*.xlsx` o `scripts/**`
- Se dispara manualmente

Para disparar manualmente:

```bash
gh workflow run dashboard.yml
```

---

## Crear el repositorio desde cero

```bash
# Crear directorio y repo
mkdir pulso-cultura-dashboard && cd pulso-cultura-dashboard
git init

# Crear estructura
mkdir -p data scripts/templates docs .github/workflows

# Copiar archivos (Excel, scripts, template, workflow)
# ...

# Crear repo en GitHub y hacer push
gh repo create THSUPER01/pulso-cultura-dashboard --public --source=. --push

# Habilitar GitHub Pages
# Settings > Pages > Deploy from branch > main > /docs

# Disparar workflow manualmente
gh workflow run dashboard.yml
```

---

## Estructura del proyecto

```
pulso-cultura-dashboard/
  .github/workflows/
    dashboard.yml          # CI/CD: genera y despliega el dashboard
  data/
    Pulso Cultura dash.xlsx  # Datos de la encuesta
  scripts/
    generate_dashboard.py    # Lee Excel, genera HTML
    templates/
      dashboard.html.j2      # Template Jinja2 del dashboard
  docs/
    dashboard.html           # Dashboard generado (self-contained)
  README.md
```

## Requisitos

- Python >= 3.9
- pandas, openpyxl, jinja2
