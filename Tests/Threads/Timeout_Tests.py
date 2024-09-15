import threading
import time

# Función genérica que ejecuta una función con timeout
def ejecutar_con_timeout(func, args=(), kwargs=None, timeout=5):
    kwargs = kwargs if kwargs else {}

    resultado = [None]  # Lista para almacenar el resultado de la función
    def wrapper():
        resultado[0] = func(*args, **kwargs)

    hilo_funcion = threading.Thread(target=wrapper)
    hilo_funcion.start()
    hilo_funcion.join(timeout)

    if hilo_funcion.is_alive():
        print(f"La función no ha terminado después de {timeout} segundos, se cancelará.")
        return None
    return resultado[0]

# Ejemplo de una función lenta
def funcion_lenta():
    time.sleep(10)
    return "Resultado de la función lenta."

# Ejecutar la función con timeout de 5 segundos
resultado = ejecutar_con_timeout(funcion_lenta, timeout=5)
print(f"Resultado de la función lenta: {resultado}")
