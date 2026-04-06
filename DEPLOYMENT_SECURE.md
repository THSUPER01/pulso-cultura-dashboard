# Guía de Despliegue Seguro en Netlify

## Resumen de Cambios

✅ **Datos individuales REMOVIDOS del HTML**
✅ **Autenticación Netlify Identity AGREGADA**
✅ **API Functions PROTEGIDA** (autorizado solo)
✅ **Datos AGREGADOS** (sin PII)

---

## Instalación Rápida

### 1. Actualizar repo

```bash
git pull origin feature/secure-auth
pip install pandas openpyxl jinja2
python scripts/generate_dashboard.py
```

### 2. Habilitar Netlify Identity

1. [Netlify Dashboard](https://app.netlify.com)
2. Site Settings → Identity → **Enable Identity**
3. Providers: Email ✅

### 3. Invitar usuarios

Identity → Users → **Invite users**
Ingresa emails de empleados

### 4. Deploy

```bash
git add -A
git commit -m "feat: Netlify Identity + Functions API for secure auth"
git push origin feature/secure-auth
```

---

## Test Local

```bash
python scripts/generate_dashboard.py
# Verifica: functions/cache/dashboard_data.json existe
```

Abre `docs/dashboard.html` → Deberías ver botón "Ingresar"

Ver TESTING_LOCAL.md para más detalles.
