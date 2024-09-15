import threading
import time

# Función que maneja los hilos
def tarea_hilo(nombre, tiempo_apagado):
    tiempo_vivo = 0
    while tiempo_vivo < tiempo_apagado:
        print(f"Hilo {nombre} sigue vivo... Tiempo: {tiempo_vivo}s")
        time.sleep(1)
        tiempo_vivo += 1
    print(f"Hilo {nombre} se apagará después de {tiempo_apagado} segundos.")

# Creación de los 3 hilos con diferentes tiempos de apagado
hilo_1 = threading.Thread(target=tarea_hilo, args=("1", 5))
hilo_2 = threading.Thread(target=tarea_hilo, args=("2", 10))
hilo_3 = threading.Thread(target=tarea_hilo, args=("3", 15))

# Iniciar los hilos
hilo_1.start()
hilo_2.start()
hilo_3.start()

# Esperar a que los hilos terminen
hilo_1.join()
hilo_2.join()
hilo_3.join()

print("Todos los hilos se han apagado.")
