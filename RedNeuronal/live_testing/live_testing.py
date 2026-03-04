import serial
import numpy as np
import tensorflow as tf


# CONFIGURACIÓN
PUERTO_SERIE = 'COM10'
BAUD_RATE = 115200

# diferentes posibilidades
# a mi me funciona mejor solo con 4 entradas (los datos del giroscopio y la presion)
CUATRO_ENTRADAS = '4_entradas'
NORMALIZADO = 'normalizado'
VARIANTES = [CUATRO_ENTRADAS]

if CUATRO_ENTRADAS in VARIANTES:
    if NORMALIZADO in VARIANTES:
        ARCHIVO_MODELO = 'modelo_figuras_lstm_norm.keras'
    else:
        ARCHIVO_MODELO = 'modelo_figuras_lstm.keras'
else:
    ARCHIVO_MODELO = 'modelo_figuras_lstm.h5'
UMBRAL_PRESION = 10
MIN_MUESTRAS = 10

# ¡CRUCIAL! Pon aquí el número de "Pasos de tiempo" que te dio el script de entrenamiento
LONGITUD_ENTRENAMIENTO = 120 


# CARGA DEL MODELO
print("Cargando modelo neuronal...")
try:
    modelo = tf.keras.models.load_model(ARCHIVO_MODELO)
    print("✅ Modelo cargado correctamente.\n")
except Exception as e:
    print(f"❌ Error al cargar el modelo: {e}")
    exit()


# MÁQUINA DE ESTADOS
def iniciar_escucha():
    try:
        puerto = serial.Serial(PUERTO_SERIE, BAUD_RATE, timeout=1)
        print(f"📡 Conectado a {PUERTO_SERIE}. ¡Empieza a dibujar!")
    except Exception as e:
        print(f"❌ Error al abrir el puerto {PUERTO_SERIE}: {e}")
        return

    buffer_trazo = []
    estado = "IDLE" # Puede ser "IDLE" (inactivo) o "RECORDING" (grabando)

    while True:
        if puerto.in_waiting > 0:
            try:
                linea = puerto.readline().decode('utf-8', errors='ignore').strip()
                if not linea:
                    continue
                
                datos_sensores = [float(x) for x in linea.split(',')]
                
                # Validamos que nos lleguen exactamente los 7 datos (ax, ay, az, gx, gy, gz, p)
                if len(datos_sensores) != 7:
                    continue

                presion = datos_sensores[6]

                # LÓGICA DE ESTADOS
                if presion > UMBRAL_PRESION:
                    if estado == "IDLE":
                        print("🔴 Trazando...", end="\r")
                        estado = "RECORDING"
                    
                    if CUATRO_ENTRADAS in VARIANTES:
                        datos_limpios = datos_sensores[3:] # omitimos las tres primeras variables
                    else:
                        datos_limpios = datos_sensores
                    buffer_trazo.append(datos_limpios)
                
                else:
                    if estado == "RECORDING":
                        # El lápiz se ha levantado, procesamos el trazo
                        if len(buffer_trazo) >= MIN_MUESTRAS:
                            print(f"\n⚡ Trazo completado ({len(buffer_trazo)} muestras). Clasificando...")
                            clasificar_trazo(buffer_trazo)
                        else:
                            print("\n⚠ Trazo demasiado corto (ignorado).")
                        
                        # Reseteamos la máquina de estados
                        buffer_trazo = []
                        estado = "IDLE"
                        print("\n🟢 Esperando siguiente trazo...")

            except ValueError:
                # Ignorar líneas basura
                pass
            except KeyboardInterrupt:
                print("\nSaliendo...")
                break


# FUNCIÓN DE PREDICCIÓN
def clasificar_trazo(trazo_lista):
    # Convertimos a formato Numpy: Shape (1, longitud_actual, 4/7)
    # Si hay que normalizar se normaliza antes
    if NORMALIZADO in VARIANTES:
        trazo_np = np.array(trazo_lista)
        trazo_norm = normalizar_trazo(trazo_np)
        trazo_listo = np.array([trazo_norm])
    else:
        trazo_np = np.array([trazo_lista])
        trazo_listo = trazo_np
    
    # Hacemos el padding para que mida exactamente lo mismo que en el entrenamiento
    trazo_padded = tf.keras.preprocessing.sequence.pad_sequences(trazo_listo, maxlen=LONGITUD_ENTRENAMIENTO, dtype='float32', padding='post', value=-999.0)
    
    prediccion_bruta = modelo.predict(trazo_padded, verbose=0)[0][0]
    
    # (0 = Círculo, 1 = Triángulo)
    if prediccion_bruta < 0.5:
        certeza = (1 - prediccion_bruta) * 100
        print(f"🎯 PREDICCIÓN: CÍRCULO (Seguridad: {certeza:.1f}%)")
    else:
        certeza = prediccion_bruta * 100
        print(f"🎯 PREDICCIÓN: TRIÁNGULO (Seguridad: {certeza:.1f}%)")

def normalizar_trazo(trazo):
    """Escala todas las columnas del trazo para que estén entre -1.0 y 1.0"""
    trazo_norm = np.copy(trazo)
    for i in range(trazo.shape[1]):
        columna = trazo[:, i]
        min_val = np.min(columna)
        max_val = np.max(columna)
        rango = max_val - min_val
        
        if rango > 0.0001: # Evitamos dividir por cero si el sensor se quedó plano
            trazo_norm[:, i] = 2.0 * ((columna - min_val) / rango) - 1.0
        else:
            trazo_norm[:, i] = 0.0
    return trazo_norm

if __name__ == "__main__":
    iniciar_escucha()