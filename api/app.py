from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import PyPDF2
import io
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# En Vercel, usar /tmp para archivos temporales (solo lectura/escritura permitida)
# Obtener el directorio raíz para templates y static
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.config['UPLOAD_FOLDER'] = '/tmp/uploads' if os.path.exists('/tmp') else os.path.join(root_dir, 'uploads')

# Configurar rutas para templates y static desde la raíz
app.template_folder = os.path.join(root_dir, 'templates')
app.static_folder = os.path.join(root_dir, 'static')

# Crear carpeta de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configurar OpenAI (puedes cambiar esto por otro modelo)
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key) if openai_api_key else None

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extrae texto de un archivo PDF"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        raise Exception(f"Error al leer el PDF: {str(e)}")

def extract_text_from_txt(file_path):
    """Extrae texto de un archivo TXT"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Intentar con otra codificación
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()

def generate_summary_long_text(text):
    """Genera resumen para textos muy largos usando estrategia de dos pasos"""
    # Dividir en secciones y resumir cada una
    sections = []
    section_size = len(text) // 3
    for i in range(3):
        start = i * section_size
        end = start + section_size if i < 2 else len(text)
        sections.append(text[start:end])
    
    # Resumir cada sección
    section_summaries = []
    for section in sections:
        try:
            prompt = f"""Resume esta sección del documento en 2-3 puntos clave. IMPORTANTE: NO copies fragmentos literales, RESUMELOS con tus propias palabras en forma de resúmenes completos:

{section[:4000]}

Puntos clave de esta sección (resúmenes, no citas):"""
            
            response = client.chat.completions.create(
                model="gpt-4",  # Usando ChatGPT GPT-4
                messages=[
                    {"role": "system", "content": "Resumes secciones de documentos de manera concisa. NUNCA copies fragmentos literales, siempre RESUMES y sintetizas las ideas principales con tus propias palabras."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0
            )
            
            section_summary = response.choices[0].message.content.strip()
            section_summaries.append(section_summary)
        except:
            pass
    
    # Combinar y crear resumen final
    combined = "\n\n".join(section_summaries)
    
    final_prompt = f"""A partir de estos resúmenes parciales, crea un resumen ejecutivo con EXACTAMENTE 5 puntos clave que capturen las ideas principales del documento completo.

IMPORTANTE: Cada punto debe ser un RESUMEN COMPLETO y coherente, no fragmentos sueltos. Expresa las ideas con claridad y profesionalismo.

Resúmenes parciales:
{combined}

Resumen ejecutivo final (5 puntos numerados, cada uno debe ser un resumen completo de 3-5 líneas):"""
    
    final_response = client.chat.completions.create(
        model="gpt-4",  # Usando ChatGPT GPT-4
        messages=[
            {"role": "system", "content": "Creas resúmenes ejecutivos consolidando información de múltiples secciones. Cada punto debe ser un resumen completo y coherente, expresado con claridad profesional, no fragmentos literales."},
            {"role": "user", "content": final_prompt}
        ],
        max_tokens=1500,  # Aumentado para permitir resúmenes más completos
        temperature=0.3
    )
    
    summary_text = final_response.choices[0].message.content.strip()
    bullets = extract_bullets_from_text(summary_text)
    return clean_and_validate_bullets(ensure_five_bullets_intelligent(bullets, text))

def clean_and_validate_bullets(bullets):
    """Limpia y valida los bullets para asegurar calidad y completitud"""
    cleaned = []
    for bullet in bullets[:5]:
        bullet = bullet.strip()
        # Eliminar prefijos comunes
        bullet = bullet.lstrip('0123456789.-•) *')
        
        # Detectar y rechazar fragmentos literales obvios
        # Si contiene comillas dobles, probablemente es una cita literal
        if '"' in bullet or bullet.count('"') >= 2:
            # Podría ser una cita, verificar si es muy corta
            if len(bullet) < 100:
                continue
        
        # Detectar referencias a páginas, capítulos, etc.
        if any(marker in bullet.lower() for marker in ['página', 'page', 'capítulo', 'chapter', '**']):
            # Si es muy corto y tiene estos marcadores, probablemente es un fragmento
            if len(bullet) < 80:
                continue
        
        # Asegurar que sea un resumen completo, no un fragmento
        if len(bullet) < 60:
            # Si es muy corto, probablemente es un fragmento incompleto
            continue
        
        # Filtrar bullets que parecen ser citas literales que empiezan con conectores
        if bullet.lower().startswith(('entonces', 'luego', 'después', 'pero', 'y ', 'o ', 'a ', 'el ', 'la ', 'los ', 'las ', 'había', 'sus ', 'un día', 'también')):
            # Podría ser un fragmento, verificar longitud
            if len(bullet) < 80:
                continue
        
        # Detectar si parece ser el inicio de una oración del texto original
        # (muchos fragmentos empiezan con mayúscula seguida de texto que parece narrativa)
        if len(bullet) < 100 and bullet[0].isupper():
            # Verificar si parece narrativa (contiene verbos en pasado típicos de narrativa)
            narrative_indicators = ['era', 'estaba', 'había', 'vio', 'encontró', 'dijo', 'pensó', 'sintió']
            if any(indicator in bullet.lower()[:50] for indicator in narrative_indicators):
                # Probablemente es un fragmento narrativo, rechazarlo si es corto
                continue
        
        # Asegurar que tenga sentido
        if not bullet.lower().startswith(('información adicional', 'aspecto adicional', 'el documento contiene')):
            # Capitalizar primera letra
            if bullet and bullet[0].islower():
                bullet = bullet[0].upper() + bullet[1:]
            # Asegurar que termine con punto si es largo
            if len(bullet) > 80 and not bullet.endswith(('.', '!', '?')):
                bullet = bullet.rstrip(',;:') + '.'
            cleaned.append(bullet)
    
    # Si tenemos menos de 5 bullets válidos, hacer una segunda pasada más permisiva
    if len(cleaned) < 5:
        for bullet in bullets:
            if len(cleaned) >= 5:
                break
            bullet = bullet.strip().lstrip('0123456789.-•) *')
            # Esta vez ser más permisivo pero aún validar
            if len(bullet) >= 40 and bullet not in cleaned:
                if bullet and bullet[0].islower():
                    bullet = bullet[0].upper() + bullet[1:]
                if len(bullet) > 80 and not bullet.endswith(('.', '!', '?')):
                    bullet = bullet.rstrip(',;:') + '.'
                cleaned.append(bullet)
    
    # Si aún tenemos menos de 5 bullets válidos, completar con resúmenes genéricos
    while len(cleaned) < 5:
        cleaned.append("El documento aborda aspectos adicionales relevantes sobre este tema que complementan la información principal.")
    
    return cleaned[:5]

def preprocess_text(text):
    """Preprocesa el texto para mejorar la calidad del resumen"""
    # Limpiar espacios múltiples
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Si el texto es muy largo, tomar una muestra representativa
    if len(text) > 15000:
        # Tomar inicio, medio y final
        third = len(text) // 3
        text = text[:5000] + "\n\n[... contenido intermedio ...]\n\n" + text[third:third+5000] + "\n\n[... contenido final ...]\n\n" + text[-5000:]
    
    return text.strip()

def generate_summary(text):
    """Genera un resumen en 5 bullets usando OpenAI"""
    if not client:
        # Si no hay API key, generar un resumen simple
        return generate_simple_summary(text)
    
    try:
        # Preprocesar el texto
        processed_text = preprocess_text(text)
        
        # Si el texto es muy largo, usar estrategia de resumen en dos pasos
        if len(processed_text) > 10000:
            return generate_summary_long_text(processed_text)
        
        prompt = f"""Eres un experto en análisis de documentos. Tu tarea es crear un resumen ejecutivo profesional.

REGLAS ABSOLUTAS:
- NUNCA copies texto literal del documento. Cada punto debe ser una SÍNTESIS completa.
- NO uses comillas ni citas del texto original.
- NO incluyas referencias a páginas, capítulos o títulos literales.
- Cada punto debe ser un RESUMEN COMPLETO de 4-6 líneas que explique una idea principal.
- Los puntos deben tener sentido independiente y ser informativos.

PROCESO:
1. Lee y comprende el documento completo
2. Identifica las 5 ideas o temas principales más importantes
3. Para cada idea, escribe un RESUMEN COMPLETO explicando qué trata, por qué es importante, y qué información clave contiene
4. Usa lenguaje profesional y claro
5. Numera: 1., 2., 3., 4., 5.

EJEMPLO DE FORMATO CORRECTO (NO copies el contenido, solo el estilo):
1. El documento relata la historia de una joven profesional que enfrenta desafíos en la gestión de sus finanzas personales debido a la falta de educación financiera en su familia.
2. Se describe cómo la protagonista intenta múltiples métodos tradicionales para organizar sus gastos, pero estos fallan debido a la falta de tiempo y conocimiento adecuado.
3. La narrativa explora los patrones familiares de manejo financiero, mostrando cómo la ausencia de conversaciones sobre dinero afecta las decisiones económicas.
4. Se presenta la solución tecnológica que la protagonista descubre, la cual promete automatizar y simplificar la gestión financiera personal.
5. El documento concluye mostrando cómo la aplicación ayuda a la protagonista a entender mejor sus finanzas y organizar su presupuesto de manera efectiva.

DOCUMENTO:

{processed_text}

Ahora crea tu resumen ejecutivo. Recuerda: RESUMIR, NO COPIAR. Cada punto debe ser un resumen completo y coherente:"""

        response = client.chat.completions.create(
            model="gpt-4",  # Usando ChatGPT GPT-4 para mejor calidad
            messages=[
                {"role": "system", "content": "Eres un experto analista de documentos profesionales. Tu trabajo es LEER, COMPRENDER y SINTETIZAR las ideas principales en resúmenes ejecutivos completos. NUNCA copias texto literal, comillas, títulos o fragmentos del documento original. Siempre creas resúmenes originales de 4-6 líneas que explican las ideas principales con tus propias palabras. Cada punto debe ser un resumen completo, coherente e informativo que tenga sentido por sí solo."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # Aumentado para permitir resúmenes más completos
            temperature=0.5
        )
        
        summary_text = response.choices[0].message.content.strip()
        
        # Extraer los bullets de manera más robusta
        bullets = extract_bullets_from_text(summary_text)
        
        # Si tenemos 5 o más bullets válidos, devolver los primeros 5
        if len(bullets) >= 5:
            return clean_and_validate_bullets(bullets[:5])
        
        # Si tenemos menos de 5, hacer una segunda llamada más específica
        if len(bullets) > 0 and len(bullets) < 5:
            try:
                remaining = 5 - len(bullets)
                completion_prompt = f"""Ya tengo {len(bullets)} puntos del resumen. Necesito {remaining} punto(s) adicional(es) que complementen y completen el análisis.

IMPORTANTE: NO copies fragmentos del texto. RESUMELOS con tus propias palabras.

Puntos actuales del resumen:
{chr(10).join(f'{i+1}. {b}' for i, b in enumerate(bullets))}

Texto original (muestra):
{processed_text[:6000]}

Proporciona EXACTAMENTE {remaining} punto(s) adicional(es) numerado(s) desde {len(bullets)+1}. Cada punto debe:
- Ser un RESUMEN completo, no una cita literal
- Cubrir un aspecto diferente del documento
- Tener sentido por sí solo (3-5 líneas)
- Estar expresado con tus propias palabras"""
                
                completion_response = client.chat.completions.create(
                    model="gpt-4",  # Usando ChatGPT GPT-4
                    messages=[
                        {"role": "system", "content": "Completas resúmenes proporcionando puntos adicionales que no repiten información. NUNCA copies fragmentos literales del texto, siempre RESUMES con tus propias palabras."},
                        {"role": "user", "content": completion_prompt}
                    ],
                    max_tokens=600,  # Aumentado para permitir resúmenes más completos
                    temperature=0.3
                )
                
                additional_text = completion_response.choices[0].message.content.strip()
                additional_bullets = extract_bullets_from_text(additional_text)
                
                # Filtrar duplicados antes de agregar
                for new_bullet in additional_bullets:
                    if len(bullets) >= 5:
                        break
                    # Verificar que no sea similar a los existentes
                    is_duplicate = False
                    for existing in bullets:
                        # Comparación simple de palabras clave
                        existing_words = set(existing.lower().split()[:5])
                        new_words = set(new_bullet.lower().split()[:5])
                        if len(existing_words.intersection(new_words)) >= 3:
                            is_duplicate = True
                            break
                    if not is_duplicate and len(new_bullet) > 20:
                        bullets.append(new_bullet)
            except Exception as e:
                pass
        
        # Si aún no tenemos 5, usar método inteligente
        final_bullets = ensure_five_bullets_intelligent(bullets, processed_text)
        return clean_and_validate_bullets(final_bullets)
    except Exception as e:
        # Fallback a resumen simple
        return generate_simple_summary(text)

def extract_bullets_from_text(text):
    """Extrae bullets de un texto de manera robusta, asegurando que sean completos"""
    bullets = []
    lines = text.split('\n')
    
    current_bullet = None
    
    for line in lines:
        line = line.strip()
        if not line:
            # Si hay un bullet en construcción, guardarlo solo si es suficientemente largo
            if current_bullet and len(current_bullet) > 60:
                bullets.append(current_bullet)
                current_bullet = None
            continue
        
        # Buscar patrones: números, guiones, viñetas
        if line and line[0].isdigit():
            # Si hay un bullet anterior, guardarlo
            if current_bullet and len(current_bullet) > 60:
                bullets.append(current_bullet)
            
            # Formato: "1. texto" o "1) texto"
            parts = line.split('.', 1) if '.' in line else line.split(')', 1)
            if len(parts) > 1:
                bullet_text = parts[1].strip()
                if bullet_text and len(bullet_text) > 20:
                    current_bullet = bullet_text
            else:
                current_bullet = line
        elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
            # Si hay un bullet anterior, guardarlo
            if current_bullet and len(current_bullet) > 60:
                bullets.append(current_bullet)
            
            bullet_text = line.lstrip('-•* ').strip()
            if bullet_text and len(bullet_text) > 20:
                current_bullet = bullet_text
        elif current_bullet:
            # Continuación del bullet anterior - sin límite de longitud
            current_bullet += " " + line
        elif len(line) > 60 and not any(char in line for char in ['http://', 'https://', '@']):
            # Línea de texto significativa que no es URL o email
            # Solo si parece un resumen completo (no un fragmento)
            if len(line) > 60 and not line.lower().startswith(('entonces', 'luego', 'pero', 'y ', 'o ', 'había', 'sus ')):
                bullets.append(line)
    
    # Guardar el último bullet si existe y es suficientemente largo
    if current_bullet and len(current_bullet) > 60:
        bullets.append(current_bullet)
    
    # Limpiar y validar bullets
    unique_bullets = []
    for bullet in bullets:
        bullet_clean = bullet.strip()
        # Asegurar que el bullet sea completo (mínimo 60 caracteres para resúmenes)
        if len(bullet_clean) < 60:
            continue
        
        # Rechazar bullets que parecen ser fragmentos literales
        # Si empieza con marcadores de formato o referencias
        if bullet_clean.startswith(('**', 'Página', 'página', 'Page', 'page', 'Capítulo', 'capítulo')):
            if len(bullet_clean) < 100:
                continue
        
        # Verificar que no sea duplicado
        is_duplicate = False
        for existing in unique_bullets:
            # Comparación más estricta
            existing_words = set(existing.lower().split()[:10])
            bullet_words = set(bullet_clean.lower().split()[:10])
            overlap = len(existing_words.intersection(bullet_words))
            if overlap >= 6:  # Muchas palabras en común = probable duplicado
                is_duplicate = True
                break
        
        if not is_duplicate:
            # No truncar - permitir resúmenes completos sin límite
            unique_bullets.append(bullet_clean)
    
    return unique_bullets

def ensure_five_bullets_intelligent(bullets, original_text):
    """Asegura exactamente 5 bullets de manera inteligente"""
    if len(bullets) >= 5:
        return bullets[:5]
    
    # Dividir el texto en párrafos significativos
    paragraphs = [p.strip() for p in original_text.split('\n\n') if len(p.strip()) > 50]
    
    # Si no hay párrafos claros, dividir por oraciones largas
    if len(paragraphs) < 3:
        sentences = [s.strip() for s in original_text.split('.') if len(s.strip()) > 40]
        # Agrupar oraciones en párrafos lógicos
        paragraphs = []
        current_para = []
        for sentence in sentences:
            current_para.append(sentence)
            if len(' '.join(current_para)) > 150:
                paragraphs.append(' '.join(current_para))
                current_para = []
        if current_para:
            paragraphs.append(' '.join(current_para))
    
    # Seleccionar párrafos más relevantes (evitar duplicados)
    used_content = set()
    for bullet in bullets:
        # Extraer palabras clave del bullet
        words = set(bullet.lower().split()[:5])
        used_content.update(words)
    
    # Buscar párrafos que no se solapen con bullets existentes
    for para in paragraphs:
        if len(bullets) >= 5:
            break
        
        # Verificar si el párrafo tiene contenido nuevo
        para_words = set(para.lower().split()[:10])
        overlap = len(para_words.intersection(used_content))
        
        # Si hay poco solapamiento, es un párrafo nuevo
        if overlap < 3 or len(used_content) == 0:
            # Crear un resumen del párrafo
            para_clean = para.strip()
            if len(para_clean) > 50:
                # Usar el párrafo completo sin truncar
                bullet = para_clean
                
                if bullet and len(bullet) > 20:
                    bullets.append(bullet)
                    used_content.update(para_words)
    
    # Si aún no tenemos 5, dividir el texto en secciones lógicas
    if len(bullets) < 5:
        # Dividir el texto en 5 secciones aproximadamente iguales
        text_length = len(original_text)
        section_size = text_length // (5 - len(bullets))
        
        for i in range(len(bullets), 5):
            start = i * section_size
            end = start + section_size
            
            # Ajustar para empezar en un punto o espacio
            if start > 0:
                while start < len(original_text) and original_text[start] not in ['.', ' ', '\n']:
                    start += 1
                start += 1
            
            section = original_text[start:end].strip()
            
            if section:
                # Usar la sección completa sin truncar
                # Encontrar la primera oración completa si es muy larga
                if '.' in section:
                    sentences = section.split('.')
                    bullet = sentences[0].strip() if sentences else section.strip()
                    # Si hay más oraciones, agregarlas también
                    if len(sentences) > 1 and len(bullet) < 300:
                        bullet += '. ' + '. '.join(sentences[1:3]).strip()
                else:
                    bullet = section.strip()
                if len(bullet) > 30:
                    bullets.append(bullet)
    
    # Garantizar exactamente 5
    while len(bullets) < 5:
        bullets.append("Información adicional relevante del documento.")
    
    return bullets[:5]

def generate_simple_summary(text):
    """Genera un resumen simple sin API (fallback) - versión mejorada"""
    # Preprocesar texto
    processed_text = preprocess_text(text)
    
    bullets = []
    
    # Dividir en párrafos significativos
    paragraphs = [p.strip() for p in processed_text.split('\n\n') if len(p.strip()) > 80]
    
    # Si hay párrafos claros, analizar cada uno
    if len(paragraphs) >= 3:
        # Priorizar párrafos del inicio, medio y final
        important_indices = [0]
        if len(paragraphs) > 1:
            important_indices.append(len(paragraphs)//3)
        if len(paragraphs) > 2:
            important_indices.append(2*len(paragraphs)//3)
        if len(paragraphs) > 3:
            important_indices.append(len(paragraphs)//2)
        if len(paragraphs) > 4:
            important_indices.append(len(paragraphs)-1)
        
        for idx in important_indices[:5]:
            if idx < len(paragraphs):
                para = paragraphs[idx]
                # Extraer la idea principal: usar el párrafo completo o las primeras oraciones
                sentences = [s.strip() for s in para.split('.') if len(s.strip()) > 40]
                if sentences:
                    # Tomar las primeras 2-3 oraciones para un resumen completo
                    if len(sentences) >= 3:
                        main_sentence = '. '.join(sentences[:3]) + '.'
                    elif len(sentences) >= 2:
                        main_sentence = '. '.join(sentences[:2]) + '.'
                    else:
                        main_sentence = sentences[0]
                    bullets.append(main_sentence)
    else:
        # Si hay pocos párrafos, trabajar con oraciones distribuidas
        sentences = [s.strip() for s in processed_text.split('.') if len(s.strip()) > 40]
        
        if len(sentences) >= 5:
            # Distribuir uniformemente
            step = max(1, len(sentences) // 5)
            for i in range(0, len(sentences), step):
                if len(bullets) >= 5:
                    break
                sentence = sentences[i]
                # No truncar - usar la oración completa
                bullets.append(sentence)
        elif len(sentences) > 0:
            # Tomar las oraciones disponibles distribuidas
            step = max(1, len(sentences) // min(5, len(sentences)))
            for i in range(0, len(sentences), step):
                if len(bullets) >= 5:
                    break
                bullets.append(sentences[i])
    
    # Asegurar exactamente 5 bullets de manera inteligente
    final_bullets = ensure_five_bullets_intelligent(bullets, processed_text)
    return clean_and_validate_bullets(final_bullets)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    """Endpoint de salud para verificar que la app funciona"""
    return jsonify({
        'status': 'ok',
        'message': 'Flask app is running',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'has_openai': client is not None
    })

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de archivo no permitido. Use PDF o TXT'}), 400
    
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extraer texto según el tipo de archivo
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_txt(file_path)
        
        if not text or len(text.strip()) < 10:
            return jsonify({'error': 'El archivo está vacío o no se pudo extraer texto'}), 400
        
        # Generar resumen
        summary = generate_summary(text)
        
        # Limpiar archivo temporal
        os.remove(file_path)
        
        return jsonify({'summary': summary})
    
    except Exception as e:
        # Limpiar archivo en caso de error
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500

# Para desarrollo local
if __name__ == '__main__':
    app.run(debug=True, port=5000)

