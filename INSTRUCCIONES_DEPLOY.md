# 🚀 Instrucciones Finales para Desplegar en Vercel

## ⚠️ PROBLEMA ACTUAL
Vercel no está instalando las dependencias de `requirements.txt`

## ✅ SOLUCIONES APLICADAS

1. ✅ Corregido `.gitignore` - Ya no ignora `requirements.txt`
2. ✅ Creado `api/requirements.txt` - Vercel busca dependencias aquí
3. ✅ Creado `runtime.txt` - Especifica versión de Python
4. ✅ `requirements.txt` en raíz - Como respaldo

## 📋 PASOS OBLIGATORIOS ANTES DE REDESPLEGAR

### 1. Verificar que requirements.txt esté en Git

```bash
# Verificar que NO está ignorado
git check-ignore requirements.txt api/requirements.txt

# Si retorna algo, significa que está ignorado
# Si retorna vacío, está bien

# Verificar que está trackeado
git ls-files requirements.txt api/requirements.txt

# Si NO aparece, agregarlo:
git add requirements.txt
git add api/requirements.txt
git add .gitignore
git commit -m "Fix: Add requirements.txt for Vercel deployment"
git push
```

### 2. Verificar estructura de archivos

Asegúrate de que tengas:
```
PruebaMantis/
├── api/
│   ├── index.py
│   └── requirements.txt  ← DEBE EXISTIR
├── app.py
├── requirements.txt      ← DEBE EXISTIR
├── runtime.txt          ← DEBE EXISTIR
├── vercel.json
├── templates/
└── static/
```

### 3. Redesplegar en Vercel

```bash
vercel --prod
```

O desde el dashboard de Vercel, haz un nuevo deployment.

### 4. Verificar los Logs del Build

En Vercel Dashboard:
1. Ve a tu proyecto
2. Deployments → Último deployment
3. Build Logs

**DEBES VER:**
```
Installing dependencies...
Collecting Flask==3.0.0
...
Successfully installed Flask-3.0.0 ...
```

**NO DEBES VER:**
```
ModuleNotFoundError: No module named 'flask'
```

## 🔄 Si AÚN Falla - Solución Alternativa

Si después de estos pasos sigue fallando, prueba esta configuración alternativa:

### Opción A: Usar solo functions (sin builds)

Reemplaza `vercel.json` con:

```json
{
  "functions": {
    "api/index.py": {
      "runtime": "python3.9"
    }
  },
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

### Opción B: Especificar installCommand explícitamente

En Vercel Dashboard:
1. Settings → General
2. Build & Development Settings
3. Install Command: `pip install -r api/requirements.txt`
4. Guardar y redesplegar

## 📞 Si Nada Funciona

1. **Verifica los logs completos** del build en Vercel
2. **Asegúrate de que `requirements.txt` esté en el repositorio** (no solo localmente)
3. **Prueba crear un proyecto nuevo** en Vercel y conectar el mismo repositorio
4. **Contacta soporte de Vercel** con los logs del error

## ✅ Checklist Final

- [ ] `requirements.txt` está en la raíz
- [ ] `api/requirements.txt` existe
- [ ] `.gitignore` NO ignora `requirements.txt`
- [ ] Archivos están commitados y pusheados a Git
- [ ] `runtime.txt` existe
- [ ] `vercel.json` está correcto
- [ ] Redesplegado en Vercel
- [ ] Revisado los logs del build

