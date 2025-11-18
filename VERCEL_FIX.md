# 🔧 Solución al Error: ModuleNotFoundError: No module named 'flask'

## Problema
Vercel no está instalando las dependencias de `requirements.txt`

## Solución Implementada

1. ✅ **requirements.txt en la raíz** - Ya existe y está correcto
2. ✅ **api/requirements.txt** - Creado como respaldo (Vercel busca aquí también)
3. ✅ **vercel.json simplificado** - Sin configuraciones conflictivas

## Pasos para Resolver

### 1. Asegúrate de que requirements.txt esté en el repositorio

Verifica que `requirements.txt` esté en la raíz y no esté en `.gitignore`:

```bash
# Verificar que existe
ls requirements.txt

# Verificar contenido
cat requirements.txt
```

### 2. Limpia el caché de Vercel y redesplega

```bash
# Eliminar el proyecto de Vercel (opcional, solo si persiste el problema)
vercel remove

# Desplegar de nuevo
vercel --prod
```

### 3. Verifica en el Dashboard de Vercel

1. Ve a tu proyecto en https://vercel.com
2. Settings → General
3. Verifica que "Install Command" esté vacío (Vercel detecta automáticamente)
4. O configura manualmente: `pip install -r requirements.txt`

### 4. Si aún no funciona - Solución Alternativa

Crea un archivo `vercel.json` con configuración explícita:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "installCommand": "pip install -r requirements.txt"
      }
    }
  ],
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

### 5. Verificar que requirements.txt no tenga errores

Asegúrate de que todas las versiones sean compatibles:

```txt
Flask==3.0.0
PyPDF2==3.0.1
openai>=1.0.0
python-dotenv==1.0.0
Werkzeug==3.0.1
```

## Archivos Creados/Modificados

- ✅ `requirements.txt` (raíz) - Dependencias principales
- ✅ `api/requirements.txt` - Copia para que Vercel la detecte
- ✅ `vercel.json` - Configuración simplificada

## Próximos Pasos

1. **Commit y push** de los cambios:
```bash
git add .
git commit -m "Fix: Add requirements.txt for Vercel deployment"
git push
```

2. **Redesplegar en Vercel**:
```bash
vercel --prod
```

3. **Verificar los logs** después del despliegue para confirmar que las dependencias se instalaron.

