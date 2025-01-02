from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__, static_folder='static')

class EscanerQRWeb:
    def __init__(self):
        self.conexion = mysql.connector.connect(
            host='localhost',
            database='empleados',
            user='root',
            password='root'
        )
        self.cursor = self.conexion.cursor(dictionary=True)

    def obtener_empleados(self):
        try:
            consulta = """SELECT id, nombre, departamento, tokens_almuerzo 
                         FROM empleados_info"""
            self.cursor.execute(consulta)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener empleados: {e}")
            return []
            
    def actualizar_empleado(self, id, nombre, departamento, tokens):
        try:
            consulta = """UPDATE empleados_info 
                         SET nombre = %s, departamento = %s, tokens_almuerzo = %s 
                         WHERE id = %s"""
            self.cursor.execute(consulta, (nombre, departamento, tokens, id))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar empleado: {e}")
            return False

@app.route('/')
def index():
    escaner = EscanerQRWeb()
    empleados = escaner.obtener_empleados()
    return render_template('tokens_intraplas.html', 
                         empleados=empleados, 
                         fecha=datetime.now().strftime('%Y-%m-%d'), 
                         hora=datetime.now().strftime('%H:%M:%S'))

@app.route('/actualizar_empleado', methods=['POST'])
def actualizar_empleado():
    escaner = EscanerQRWeb()
    id = request.form.get('id')
    nombre = request.form.get('nombre')
    departamento = request.form.get('departamento')
    tokens = request.form.get('tokens')
    
    if escaner.actualizar_empleado(id, nombre, departamento, tokens):
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True)