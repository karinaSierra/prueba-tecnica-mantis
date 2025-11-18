# 🚀 Guía de Despliegue en Vercel

Esta guía te ayudará a desplegar tu aplicación Flask en Vercel paso a paso.

## 📋 Requisitos Previos

1. **Cuenta de Vercel**: Crea una cuenta gratuita en [vercel.com](https://vercel.com)
2. **Git**: Asegúrate de tener Git instalado
3. **Vercel CLI** (opcional pero recomendado): `npm i -g vercel`

## 🔧 Paso 1: Preparar el Proyecto

El proyecto ya está configurado con los archivos necesarios:
- ✅ `vercel.json` - Configuración de Vercel
- ✅ `api/index.py` - Punto de entrada para Vercel
- ✅ `requirements.txt` - Dependencias Python

## 📝 Paso 2: Configurar Variables de Entorno

Necesitas configurar tu API key de OpenAI en Vercel:

### Opción A: Desde la Web de Vercel
1. Ve a tu proyecto en [vercel.com](https://vercel.com)
2. Ve a **Settings** → **Environment Variables**
3. Agrega:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: Tu clave de API de OpenAI
   - **Environment**: Production, Preview, Development (marca todas)

### Opción B: Desde la CLI
```bash
vercel env add OPENAI_API_KEY
# Pega tu API key cuando se solicite
```

## 🚀 Paso 3: Desplegar

### Opción A: Desde la Web de Vercel (Recomendado para principiantes)

1. **Sube tu código a GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tu-usuario/tu-repo.git
   git push -u origin main
   ```

2. **Importa el proyecto en Vercel**:
   - Ve a [vercel.com/new](https://vercel.com/new)
   - Conecta tu cuenta de GitHub
   - Selecciona el repositorio
   - Vercel detectará automáticamente la configuración
   - Haz clic en **Deploy**

3. **Configura las variables de entorno** (si no lo hiciste antes):
   - En la página del proyecto, ve a **Settings** → **Environment Variables**
   - Agrega `OPENAI_API_KEY` con tu clave

### Opción B: Desde la CLI de Vercel

1. **Instala Vercel CLI** (si no lo tienes):
   ```bash
   npm install -g vercel
   ```

2. **Inicia sesión**:
   ```bash
   vercel login
   ```

3. **Despliega**:
   ```bash
   vercel
   ```
   
   Sigue las instrucciones:
   - ¿Set up and deploy? → **Y**
   - ¿Which scope? → Selecciona tu cuenta
   - ¿Link to existing project? → **N** (primera vez)
   - ¿Project name? → Presiona Enter (usa el nombre por defecto)
   - ¿Directory? → Presiona Enter (usa el directorio actual)

4. **Configura variables de entorno**:
   ```bash
   vercel env add OPENAI_API_KEY
   ```

5. **Despliega a producción**:
   ```bash
   vercel --prod
   ```

## ✅ Paso 4: Verificar el Despliegue

1. Vercel te dará una URL como: `https://tu-proyecto.vercel.app`
2. Abre la URL en tu navegador
3. Prueba subir un archivo PDF o TXT
4. Verifica que el resumen se genere correctamente

## 🔄 Paso 5: Actualizaciones Futuras

Cada vez que hagas cambios:

### Con Git (Recomendado):
```bash
git add .
git commit -m "Descripción de cambios"
git push
```
Vercel desplegará automáticamente si tienes integración con GitHub.

### Con CLI:
```bash
vercel --prod
```

## 🐛 Solución de Problemas

### Error: "Module not found"
- Verifica que todas las dependencias estén en `requirements.txt`
- Asegúrate de que `vercel.json` esté configurado correctamente

### Error: "OPENAI_API_KEY not found"
- Verifica que hayas configurado la variable de entorno en Vercel
- Asegúrate de haber seleccionado todos los ambientes (Production, Preview, Development)

### Error: "File upload failed"
- Vercel tiene límites de tamaño para funciones serverless
- El límite actual es 4.5MB para el body de la request
- Considera reducir el tamaño máximo de archivo en `app.py` si es necesario

### La aplicación no carga
- Verifica los logs en Vercel: **Deployments** → Selecciona el deployment → **Functions** → Ver logs
- Revisa que la ruta `/api/index.py` esté correctamente configurada

## 📊 Límites de Vercel (Plan Gratuito)

- **Tiempo de ejecución**: 10 segundos (Hobby), 60 segundos (Pro)
- **Tamaño de función**: 50MB
- **Memoria**: 1024MB
- **Ancho de banda**: 100GB/mes

## 💡 Consejos

1. **Monitorea los logs**: Usa el dashboard de Vercel para ver errores en tiempo real
2. **Prueba localmente**: Usa `vercel dev` para probar localmente antes de desplegar
3. **Optimiza el código**: Para textos muy largos, considera procesarlos en chunks
4. **Usa caché**: Considera cachear resúmenes si procesas los mismos documentos frecuentemente

## 🔗 Enlaces Útiles

- [Documentación de Vercel](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Dashboard de Vercel](https://vercel.com/dashboard)

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en el dashboard de Vercel
2. Consulta la [documentación de Vercel](https://vercel.com/docs)
3. Revisa los [foros de Vercel](https://github.com/vercel/vercel/discussions)

¡Listo! Tu aplicación debería estar funcionando en Vercel. 🎉

