from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import logging
import uuid
import zipfile
import io

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuración
DB_CONFIG = {
    'host': 'localhost',
    'database': 'nasa',
    'user': 'root',
    'password': ''
}

# Configuración de carpetas
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'csv', 'json'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Crear carpeta de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error conectando a MySQL: {e}")
        return None

def allowed_file(filename):
    """Verificar si la extensión del archivo es permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file_to_disk(file):
    """Guardar archivo en el sistema de archivos y retornar la ruta"""
    try:
        # Generar nombre único para evitar colisiones
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Guardar archivo
        file.save(file_path)
        return file_path, unique_filename
        
    except Exception as e:
        logger.error(f"Error guardando archivo: {e}")
        return None, None

@app.route('/upload', methods=['POST'])
def upload_files():
    """Endpoint para subir archivos"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No se encontraron archivos'}), 400
        
        files = request.files.getlist('files')
        donador = request.form.get('donador', 'Anónimo')
        descripcion = request.form.get('description', '')
        consentimiento = request.form.get('consent') == 'true'
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'No se seleccionaron archivos'}), 400
        
        if not consentimiento:
            return jsonify({'error': 'Debe aceptar los términos de uso'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor()
        archivos_subidos = []
        archivos_con_error = []
        
        for file in files:
            # Validar tipo de archivo
            if not allowed_file(file.filename):
                archivos_con_error.append({
                    'nombre': file.filename,
                    'error': 'Tipo de archivo no permitido'
                })
                continue
            
            # Validar tamaño
            file.seek(0, 2)  # Ir al final
            file_size = file.tell()
            file.seek(0)  # Volver al inicio
            
            if file_size > MAX_FILE_SIZE:
                archivos_con_error.append({
                    'nombre': file.filename,
                    'error': 'Archivo demasiado grande'
                })
                continue
            
            # Guardar archivo en carpeta
            file_path, unique_filename = save_file_to_disk(file)
            if not file_path:
                archivos_con_error.append({
                    'nombre': file.filename,
                    'error': 'Error guardando archivo'
                })
                continue
            
            # Insertar metadata en la base de datos
            sql = """
            INSERT INTO documentos_exoplanetas 
            (nombre_archivo, tipo_archivo, tamano_archivo, ruta_archivo, donador, descripcion, consentimiento)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            
            cursor.execute(sql, (
                file.filename,          # Nombre original
                file_extension,         # Extensión
                file_size,              # Tamaño
                file_path,              # Ruta en el servidor
                donador,                # Donador
                descripcion,            # Descripción
                consentimiento          # Consentimiento
            ))
            
            archivos_subidos.append({
                'nombre': file.filename,
                'tipo': file_extension,
                'tamano': file_size,
                'ruta': unique_filename
            })
        
        connection.commit()
        cursor.close()
        connection.close()
        
        response_data = {
            'message': f'Se subieron {len(archivos_subidos)} archivos correctamente',
            'archivos': archivos_subidos
        }
        
        if archivos_con_error:
            response_data['errores'] = archivos_con_error
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error en upload_files: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/descargar-todos', methods=['GET'])
def descargar_todos_documentos():
    """Endpoint para descargar todos los documentos en un ZIP"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre_archivo, ruta_archivo FROM documentos_exoplanetas")
        
        documentos = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if not documentos:
            return jsonify({'error': 'No hay documentos disponibles'}), 404
        
        # Crear archivo ZIP en memoria
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for documento in documentos:
                if os.path.exists(documento['ruta_archivo']):
                    # Agregar archivo al ZIP
                    zip_file.write(
                        documento['ruta_archivo'], 
                        documento['nombre_archivo']
                    )
        
        zip_buffer.seek(0)
        
        # Enviar ZIP
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"documentos_exoplanetas_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"Error en descargar_todos_documentos: {e}")
        return jsonify({'error': 'Error al crear el archivo ZIP'}), 500
    
@app.route('/api/total-archivos', methods=['GET'])
def total_archivos():
    """Endpoint simple para obtener solo el total de archivos"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión'}), 500
        
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM documentos_exoplanetas")
        total = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'total_archivos': total
        }), 200
        
    except Exception as e:
        logger.error(f"Error en total-archivos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/total-donadores', methods=['GET'])
def total_donadores():
    """Endpoint simple para obtener solo el total de donadores"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión'}), 500
        
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(DISTINCT donador) as total FROM documentos_exoplanetas")
        total = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'total_donadores': total
        }), 200
        
    except Exception as e:
        logger.error(f"Error en total-donadores: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)