# Importación de las librerías necesarias
from flask import Flask, render_template, request  # Flask para el servidor web, render_template para renderizar HTML, y request para recibir datos de formularios
import pymysql  # Librería para conectar con MySQL

# Crear la instancia principal de Flask
app = Flask(__name__, template_folder='templates')

# Clave secreta para proteger sesiones y formularios
app.secret_key = 'secretkey'

# Función para establecer una conexión con la base de datos
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',       # Dirección del servidor MySQL
        user='root',            # Usuario de MySQL
        password='',            # Contraseña vacía
        db='prueba_1',          # Nombre de la base de datos
        cursorclass=pymysql.cursors.DictCursor  # Devolver resultados como diccionarios
    )

# Ruta principal que carga el menú de inicio (index.html)
@app.route('/')
def home():
    return render_template('index.html')  # Renderiza la plantilla HTML de inicio

# Ruta para registrar usuarios, permite métodos GET y POST
@app.route('/register', methods=['GET', 'POST'])
def register():
    mensaje = ''  # Variable para mostrar mensajes al usuario

    if request.method == 'POST':  # Si el formulario fue enviado (POST)
        # Obtener los datos del formulario
        nombre_completo = request.form['nombre_completo']
        correo = request.form['correo']
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        estado = request.form['estado']
        rol_nombre = request.form['rol_id']  # Valor textual del rol: 'Usuario' o 'Administrador'

        # Conectar a la base de datos
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Buscar el ID del rol según su nombre
                cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol_nombre,))
                rol_data = cur.fetchone()

                if not rol_data:
                    # Si no se encuentra el rol, mostrar error
                    mensaje = 'Error: el rol seleccionado no existe.'
                else:
                    rol_id = rol_data['id']  # Obtener el ID del rol

                    # Verificar si el usuario o el correo ya existen en la base de datos
                    cur.execute("SELECT * FROM usuarios WHERE usuario = %s OR correo = %s", (usuario, correo))
                    if cur.fetchone():
                        mensaje = 'Ya existe un usuario o correo registrado.'
                    else:
                        # Insertar el nuevo usuario con 0 intentos fallidos
                        cur.execute("""
                            INSERT INTO usuarios 
                            (nombre_completo, correo, usuario, contraseña, estado, intentos_fallidos, rol_id) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (nombre_completo, correo, usuario, contraseña, estado, 0, rol_id))
                        conn.commit()  # Confirmar los cambios en la base de datos
                        mensaje = '¡Usuario registrado exitosamente!'
        finally:
            conn.close()  # Cerrar la conexión a la base de datos

    # Mostrar el formulario de registro y cualquier mensaje
    return render_template('register.html', mensaje=mensaje)

# Ejecutar la aplicación Flask en modo debug
if __name__ == '__main__':
    app.run(debug=True)