from flask import Flask, render_template
import mysql.connector
from datetime import datetime
import time 

app = Flask(__name__)

app = Flask(__name__, static_folder='static') # Establece la carpeta "media" como carpeta de recursos estáticos

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

@app.route('/')
def index():
    escaner = EscanerQRWeb()
    empleados = escaner.obtener_empleados()
    return render_template('tokens_intraplas.html', empleados=empleados, fecha=datetime.now().strftime('%Y-%m-%d'), hora=datetime.now().strftime('%H:%M:%S'))

if __name__ == '__main__':
    app.run(debug=True)