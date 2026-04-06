# Pulso Cultura Dashboard - Arquitectura de Seguridad

## Descripción General

Este dashboard implementa una arquitectura **segura de dos capas** que protege los datos de la encuesta:

1. **Frontend (HTML estático)**: Interfaz pública sin datos sensibles incrustados
2. **Backend (Netlify Functions)**: API autenticada que retorna datos agregados (sin registros individuales)

---

## Cambios Implementados

### 1. Eliminación de Datos Individuales del HTML

**Antes (INSEGURO):**
```javascript
// ❌ Todos los registros de encuesta en el HTML
const DASHBOARD_DATA = {
  records: [
    { id: 123, genero: "M", edad: "30-39", respuestas: [...] },
    { id: 124, genero: "F", edad: "25-30", respuestas: [...] },
    // ... 500+ registros visibles en el source
  ]
}
```

**Ahora (SEGURO):**
```javascript
// ✅ Solo metadata + filter options (sin registros individuales)
const DASHBOARD_DATA = {
  questions: [
    { key: "q0", text: "¿...", variable: "Cuidado", dimension: "Respeto" }
  ],
  filterOptions: {
    genero: ["Femenino", "Masculino"],
    edad: ["18-25", "26-35", ...]
  }
  // NO records individuales
}
```

### 2. Autenticación con Netlify Identity

**Flujo:**
1. Usuario carga dashboard
2. Netlify Identity widget abre modal de login
3. Usuario ingresa credenciales
4. Si autenticado → Token JWT obtenido
5. JavaScript fetch con `Authorization: Bearer {token}`
6. Netlify Function valida token

### 3. Netlify Functions para Datos Agregados

**Nueva función:** `/.netlify/functions/dashboard`
- Verifica autenticación (token JWT)
- Lee archivo `functions/cache/dashboard_data.json`
- Retorna: questions, filterOptions, aggregates SOLAMENTE

---

## Configuración Netlify Identity

### En Netlify Dashboard:
1. Site Settings → Identity → Enable Identity
2. Providers: Email/Password, Gmail, GitHub (opcionales)
3. Users: Invita usuarios con sus emails

---

## Mejoras Futuras

- [ ] Rate limiting en Netlify Functions
- [ ] Encryption at rest para Excel source  
- [ ] Audit logging de descargas
- [ ] SSO corporativo (SAML/OIDC)
- [ ] Two-factor authentication (2FA)
- [ ] Entitlements por rol

Ver DEPLOYMENT_SECURE.md para más detalles.
