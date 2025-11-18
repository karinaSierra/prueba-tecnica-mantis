# 📄 Resumen Inteligente de Documentos

Una aplicación web sencilla que permite subir archivos PDF o de texto y generar un resumen automático en 5 puntos clave usando inteligencia artificial.

## 🚀 Características

- Interfaz moderna y responsive
- Soporte para archivos PDF y TXT
- Drag & drop para subir archivos
- Resumen automático en 5 bullets usando IA
- Procesamiento rápido y eficiente

## 📋 Requisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. Clona o descarga este repositorio

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. (Opcional) Configura tu API key de OpenAI:
   - Crea un archivo `.env` en la raíz del proyecto
   - Agrega tu clave: `OPENAI_API_KEY=tu_clave_aqui`
   - Si no proporcionas una clave, la aplicación usará un resumen simple sin IA

## 🎯 Uso

1. Inicia el servidor:
```bash
python app.py
```

2. Abre tu navegador en: `http://localhost:5000`

3. Sube un archivo PDF o TXT (arrastra o haz clic para seleccionar)

4. Haz clic en "Generar Resumen"

5. ¡Listo! Verás el resumen en 5 puntos clave

## 📁 Estructura del Proyecto

```
PruebaMantis/
├── app.py                 # Servidor Flask
├── requirements.txt       # Dependencias Python
├── templates/
│   └── index.html        # Página principal
├── static/
│   ├── style.css         # Estilos
│   └── script.js         # JavaScript del frontend
├── uploads/              # Carpeta temporal para archivos (se crea automáticamente)
└── README.md            # Este archivo
```

## 🔑 Obtener API Key de OpenAI

1. Ve a https://platform.openai.com/
2. Crea una cuenta o inicia sesión
3. Ve a API Keys en tu perfil
4. Genera una nueva clave
5. Cópiala en tu archivo `.env`

## ⚙️ Configuración

- **Tamaño máximo de archivo**: 16MB (configurable en `app.py`)
- **Modelo de IA**: GPT-4 (ChatGPT) (configurable en `app.py`)
- **Puerto**: 5000 (configurable en `app.py`)

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **IA**: OpenAI API (opcional)
- **Procesamiento PDF**: PyPDF2

## 📝 Notas

- Los archivos subidos se eliminan automáticamente después del procesamiento
- Si no tienes API key de OpenAI, la aplicación funcionará con un resumen básico
- La aplicación está optimizada para documentos en español

## 🐛 Solución de Problemas

- **Error al subir archivo**: Verifica que el archivo sea PDF o TXT y no exceda 16MB
- **Error de API**: Verifica que tu clave de OpenAI sea válida y tenga créditos
- **Puerto en uso**: Cambia el puerto en `app.py` si el 5000 está ocupado

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.


