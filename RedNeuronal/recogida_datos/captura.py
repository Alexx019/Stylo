import serial
import csv
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# CONFIGURACIÓN
PUERTO_SERIE = 'COM10'
BAUD_RATE = 115200

class GrabadorGiroscopio:
    def __init__(self, root):
        self.root = root
        self.root.title("Grabador de Datos del Giroscopio")
        self.root.geometry("350x250")
        
        # variables de estado
        self.grabando = False
        self.archivo_csv = None
        self.writer_csv = None
        self.puerto_serie = None
        
        # menú
        tk.Label(root, text="Selecciona la figura a grabar:", font=("Arial", 12)).pack(pady=10)
        
        self.btn_circulos = tk.Button(root, text="🔴 Iniciar Grabación: CÍRCULOS", bg="lightblue", command=lambda: self.iniciar_grabacion("circulos"))
        self.btn_circulos.pack(pady=5, fill=tk.X, padx=20)
        
        self.btn_triangulos = tk.Button(root, text="🔺 Iniciar Grabación: TRIÁNGULOS", bg="lightgreen", command=lambda: self.iniciar_grabacion("triangulos"))
        self.btn_triangulos.pack(pady=5, fill=tk.X, padx=20)
        
        self.btn_parar = tk.Button(root, text="⏹ PARAR GRABACIÓN", bg="salmon", state=tk.DISABLED, command=self.parar_grabacion)
        self.btn_parar.pack(pady=15, fill=tk.X, padx=20)
        
        self.lbl_estado = tk.Label(root, text="Estado: Esperando...", font=("Arial", 10, "italic"))
        self.lbl_estado.pack(pady=10)

        # conexión serial
        self.conectar_serie()

    def conectar_serie(self):
        try:
            self.puerto_serie = serial.Serial(PUERTO_SERIE, BAUD_RATE, timeout=1)
            # hilo que leerá el puerto serial constantemente
            hilo_lectura = threading.Thread(target=self.leer_datos_serie, daemon=True)
            hilo_lectura.start()
        except serial.SerialException:
            messagebox.showerror("Error", f"No se pudo conectar al puerto {PUERTO_SERIE}")
            self.root.destroy()

    def iniciar_grabacion(self, figura):
        # desactivar botones de inicio y activar el de parar
        self.btn_circulos.config(state=tk.DISABLED)
        self.btn_triangulos.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        
        # archivo CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"datos_{figura}_{timestamp}.csv"
        
        self.archivo_csv = open(nombre_archivo, mode='w', newline='')
        self.writer_csv = csv.writer(self.archivo_csv)
        
        # primera linea
        self.writer_csv.writerow(['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'p']) 
        
        self.grabando = True
        self.figura_actual = figura
        self.lbl_estado.config(text=f"Estado: GRABANDO {figura.upper()}...", fg="red")

    def parar_grabacion(self):
        self.grabando = False
        
        if self.archivo_csv:
            self.archivo_csv.close()
            
        self.btn_parar.config(state=tk.DISABLED)
        self.lbl_estado.config(text=f"Estado: Grabación de {self.figura_actual} terminada.", fg="black")
        
        # Restaurar el botón de la figura que NO se ha grabado todavía
        if self.figura_actual == "circulos":
            self.btn_triangulos.config(state=tk.NORMAL)
            # El botón de círculos se queda deshabilitado para siempre en esta sesión
        elif self.figura_actual == "triangulos":
            self.btn_circulos.config(state=tk.NORMAL)
            # El botón de triángulos se queda deshabilitado para siempre en esta sesión

    def leer_datos_serie(self):
        while True:
            if self.puerto_serie and self.puerto_serie.in_waiting > 0:
                try:
                    linea = self.puerto_serie.readline().decode('utf-8').strip()
                    # Si estamos grabando, guardamos los datos
                    if self.grabando and self.writer_csv:
                        # Arduino envía datos separados por coma
                        datos = linea.split(',')
                        self.writer_csv.writerow(datos)
                except Exception as e:
                    print(f"Error leyendo datos: {e}")

if __name__ == "__main__":
    ventana = tk.Tk()
    app = GrabadorGiroscopio(ventana)
    ventana.mainloop()