# 🚀 Guía de Despliegue en Vercel

## Paso a Paso para Desplegar en Vercel

### 1. Preparación del Proyecto

El proyecto ya está configurado con los archivos necesarios:
- ✅ `vercel.json` - Configuración de Vercel
- ✅ `api/index.py` - Wrapper para serverless functions
- ✅ `requirements.txt` - Dependencias Python
- ✅ `.vercelignore` - Archivos a ignorar

### 2. Instalar Vercel CLI (si no lo tienes)

```bash
npm install -g vercel
```

O si prefieres usar npx:
```bash
npx vercel
```

### 3. Iniciar Sesión en Vercel

```bash
vercel login
```

Sigue las instrucciones para autenticarte.

### 4. Desplegar el Proyecto

Desde la raíz del proyecto (`C:\PruebaMantis`):

```bash
vercel
```

O para producción directamente:

```bash
vercel --prod
```

### 5. Configurar Variables de Entorno

Después del despliegue, configura tu API key de OpenAI:

**Opción A: Desde la CLI**
```bash
vercel env add OPENAI_API_KEY
```
Ingresa tu clave cuando se solicite.

**Opción B: Desde el Dashboard de Vercel**
1. Ve a tu proyecto en https://vercel.com
2. Settings → Environment Variables
3. Agrega `OPENAI_API_KEY` con tu clave de OpenAI
4. Selecciona los ambientes (Production, Preview, Development)
5. Guarda y redespiega

### 6. Redesplegar (si agregaste variables de entorno)

```bash
vercel --prod
```

### 7. Verificar el Despliegue

Una vez desplegado, Vercel te dará una URL como:
- `https://tu-proyecto.vercel.app`

Visita la URL para verificar que todo funciona.

## 📝 Notas Importantes

### Archivos Temporales
- En Vercel, los archivos se guardan en `/tmp/uploads` (solo lectura/escritura permitida)
- Los archivos se eliminan automáticamente después de cada request

### Límites de Vercel
- **Timeout**: 10 segundos (Hobby), 60 segundos (Pro)
- **Tamaño de función**: 50MB (Hobby), 250MB (Pro)
- **Memoria**: 1024MB (Hobby), 3008MB (Pro)

### Si tienes problemas:

1. **Error de build**: Verifica que `requirements.txt` tenga todas las dependencias
2. **Error de importación**: Asegúrate de que `api/index.py` esté correctamente configurado
3. **Error de variables de entorno**: Verifica que `OPENAI_API_KEY` esté configurada
4. **Timeout**: Considera optimizar el procesamiento o usar un plan Pro

## 🔄 Actualizar el Despliegue

Cada vez que hagas cambios:

```bash
git add .
git commit -m "Descripción de cambios"
vercel --prod
```

O simplemente:
```bash
vercel --prod
```

## 📚 Recursos

- [Documentación de Vercel Python](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel CLI Docs](https://vercel.com/docs/cli)

