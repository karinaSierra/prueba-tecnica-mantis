# 🔧 Solución de Problemas - Vercel

## Error 500: FUNCTION_INVOCATION_FAILED

Si estás viendo este error, sigue estos pasos:

### 1. Ver los Logs de Vercel

**Opción A: Desde el Dashboard**
1. Ve a https://vercel.com
2. Selecciona tu proyecto
3. Ve a la pestaña "Deployments"
4. Haz clic en el deployment que falló
5. Ve a "Functions" → "View Function Logs"

**Opción B: Desde la CLI**
```bash
vercel logs [tu-url].vercel.app
```

### 2. Problemas Comunes y Soluciones

#### Problema: Error de importación
**Síntoma**: `ModuleNotFoundError` o `ImportError` en los logs

**Solución**:
- Verifica que `requirements.txt` tenga todas las dependencias
- Asegúrate de que no falten dependencias transitivas

#### Problema: No encuentra templates o static
**Síntoma**: `TemplateNotFound` o archivos estáticos no cargan

**Solución**: Ya está configurado con `os.chdir(root_dir)` en `api/index.py`

#### Problema: Error con /tmp
**Síntoma**: `PermissionError` o `FileNotFoundError` con `/tmp`

**Solución**: Ya está configurado para usar `/tmp/uploads` en Vercel

#### Problema: Timeout
**Síntoma**: La función tarda más de 10 segundos (plan gratuito)

**Solución**:
- Optimiza el procesamiento
- Considera usar un plan Pro (60 segundos de timeout)
- O divide el procesamiento en pasos más pequeños

### 3. Verificar la Configuración

Asegúrate de que estos archivos existan y estén correctos:

✅ `vercel.json` - Configuración de Vercel
✅ `api/index.py` - Handler para serverless functions
✅ `requirements.txt` - Todas las dependencias
✅ `app.py` - Aplicación Flask principal

### 4. Probar Localmente con Vercel Dev

```bash
vercel dev
```

Esto simula el entorno de Vercel localmente y te ayudará a identificar problemas.

### 5. Redesplegar

Después de hacer cambios:

```bash
vercel --prod
```

### 6. Si el Problema Persiste

1. **Revisa los logs específicos** - Los logs te dirán exactamente qué está fallando
2. **Verifica las variables de entorno** - Asegúrate de que `OPENAI_API_KEY` esté configurada
3. **Prueba con un endpoint simple** - Crea una ruta de prueba para verificar que Flask funciona

Ejemplo de ruta de prueba en `app.py`:
```python
@app.route('/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Flask is working'})
```

### 7. Contactar Soporte

Si nada funciona, puedes:
- Revisar la documentación: https://vercel.com/docs
- Contactar soporte de Vercel
- Revisar los issues en GitHub de Vercel

