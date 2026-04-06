# Testing Local - Verificar Arquitectura

## 1. Validación Script Python

```bash
cd c:\Repos\pulso-cultura-dashboard
python scripts/generate_dashboard.py
```

**Output esperado:**
- ✅ `functions/cache/dashboard_data.json` creado
- ✅ `docs/dashboard.html` generado (sin records)

## 2. Verificaciones de Seguridad

### Sin registros individuales en HTML
```bash
grep -c "id.*:" docs/dashboard.html | grep -v "getElementById"
# Output: 0
```

### Con Netlify Identity widget
```bash
grep "netlifyIdentity" docs/dashboard.html
# Output: >= 1
```

### Con datos agregados en cache
```bash
grep -c "favorabilidad" functions/cache/dashboard_data.json
# Output: >= 1
```

---

## 3. Test en Navegador

Abre: `docs/dashboard.html`

Deberías ver:
- 🔒 Botón "Ingresar" (Netlify Identity)
- Form de login
- ❌ NO datos sin autenticar

---

## 4. Checklist Final

- [ ] `functions/dashboard.js` existe
- [ ] `functions/shared/auth.js` existe
- [ ] `functions/cache/` directorio existe
- [ ] `netlify.toml` tiene `[identity]`
- [ ] `scripts/templates/dashboard.html.j2` contiene `netlifyIdentity`
- [ ] `grep -c "id" functions/cache/dashboard_data.json = 0`
- [ ] SECURITY.md creado
- [ ] DEPLOYMENT_SECURE.md creado

Ver DEPLOYMENT_SECURE.md para Netlify setup.
