from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__, static_folder='static')

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'empleados'

mysql = MySQL(app)

class EscanerQRWeb:
    def __init__(self, mysql):
        self.mysql = mysql

    def obtener_empleados(self):
        try:
            cur = self.mysql.connection.cursor()
            consulta = """SELECT id, nombre, departamento, tokens_almuerzo 
                         FROM empleados_info"""
            cur.execute(consulta)
            # Obtener los nombres de las columnas
            columns = [desc[0] for desc in cur.description]
            # Convertir los resultados a una lista de diccionarios
            empleados = []
            for row in cur.fetchall():
                empleado = {}
                for i, column in enumerate(columns):
                    empleado[column] = row[i]
                empleados.append(empleado)
            cur.close()
            print("Datos obtenidos:", empleados)  # Para debug
            return empleados
        except Exception as e:
            print(f"Error al obtener empleados: {e}")
            return []
            
    def actualizar_empleado(self, id, nombre, departamento, tokens):
        try:
            cur = self.mysql.connection.cursor()
            consulta = """UPDATE empleados_info 
                         SET nombre = %s, departamento = %s, tokens_almuerzo = %s 
                         WHERE id = %s"""
            cur.execute(consulta, (nombre, departamento, tokens, id))
            self.mysql.connection.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error al actualizar empleado: {e}")
            return False

    def obtener_total_empleados(self):
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT COUNT(*) FROM empleados_info')
            total = cur.fetchone()[0]
            cur.close()
            return total
        except Exception as e:
            print(f"Error al obtener total de empleados: {e}")
            return 0

@app.route('/empleados')
def index():
    escaner = EscanerQRWeb(mysql)
    empleados = escaner.obtener_empleados()
    total_empleados = escaner.obtener_total_empleados()
    print("Empleados en la ruta:", empleados)  # Para debug
    return render_template('tokens_intraplas.html', 
                         empleados=empleados,
                         total_empleados=total_empleados,
                         fecha=datetime.now().strftime('%Y-%m-%d'), 
                         hora=datetime.now().strftime('%H:%M:%S'))


@app.route('/registrar', methods=['POST'])
def registrar():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    fullname = request.form.get('fullname')
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuarios (username, password, email, fullname) VALUES (%s, %s, %s, %s)", 
                (username, password, email, fullname))
    mysql.connection.commit()
    cur.close()
    
    return render_template('login.html', redirect_url='/')


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/Dashboard')
def dashboard():
    escaner = EscanerQRWeb(mysql)
    total_usuarios = escaner.obtener_total_empleados()
    return render_template('Dashboard.html', total_usuarios=total_usuarios)

@app.route('/api/total-usuarios')
def obtener_total_usuarios():
    escaner = EscanerQRWeb(mysql)
    total = escaner.obtener_total_empleados()
    return jsonify({'total': total})

@app.route('/actualizar_empleado', methods=['POST'])
def actualizar_empleado_route():
    escaner = EscanerQRWeb(mysql)
    id = request.form.get('id')
    nombre = request.form.get('nombre')
    departamento = request.form.get('departamento')
    tokens = request.form.get('tokens')
    
    if escaner.actualizar_empleado(id, nombre, departamento, tokens):
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True)