import threading
import time
import random
from colorama import Fore, Style, Back, init

init()
NUM_SILLAS = 5     # Número de sillas en la sala de espera
num_clientes = 20  # Número total de clientes
barbero_durmiendo = True # Variable para ver si el barbero esta durmiendo o no.
entra_cliente = threading.Semaphore(0) # Control para esperar a que entre un cliente
id_cliente_aviso = 0 # Variable para saber que cliente le aviso al otro.
aviso = threading.Semaphore(0) # Control para esperar el aviso
cliente_listo = threading.Semaphore(0) # Control para esperar a que el cliente este listo para recorte
barbero_listo = threading.Semaphore(0) # Control para esperar a que el barbero este listo para recortar
cliente_atendido = threading.Semaphore(0) # Semáforo contador para indicar que el cliente ha sido atendido
clientes_en_espera = 0  # Contador de clientes en espera

def cliente(id):
    global clientes_en_espera
    global barbero_durmiendo
    global id_cliente_aviso
    time.sleep(random.uniform(0, 10))   # El cliente tarda un tiempo aleatorio en llegar
    if clientes_en_espera == NUM_SILLAS: # El cliente revisa si esta lleno el local
        print(f"{Fore.RED}Cliente {id} se va sin pelarse porque no hay sillas disponibles. {Style.RESET_ALL}")
        return # Si esta lleno entonces se retira.

    if(barbero_durmiendo):
        entra_cliente.release()
        print(f"{Fore.GREEN}Cliente {id} llega, ve que hay ({clientes_en_espera}/{NUM_SILLAS} sillas ocupadas). Despierta al barbero {Style.RESET_ALL}")
        clientes_en_espera += 1 # El cliente se une a la cola hasta que el barbero se prepare.
        barbero_durmiendo=False # El cliente despierta al barbero
        barbero_listo.acquire() # Esperamos a que el barbero este listo
    else:
        clientes_en_espera += 1 # El cliente se une a la Cola
        print(f"{Fore.YELLOW}Cliente {id} llega y se sienta a esperar. Ahora hay ({clientes_en_espera}/{NUM_SILLAS} sillas ocupadas). {Style.RESET_ALL}")
        aviso.acquire() # Esperamos el aviso del cliente que estan recortando
        barbero_listo.acquire() # Esperamos a que el barbero se prepare 
        print(f"{Fore.YELLOW}Cliente {id} Recibio el aviso de {id_cliente_aviso} y pasa a recortarse. Ahora hay ({clientes_en_espera-1}/{NUM_SILLAS} sillas ocupadas). {Style.RESET_ALL}")

    id_cliente_aviso = id # Guardamos el cliente que se esta recortando ahora mismo
    clientes_en_espera -= 1   # Indicamos que ya no estamos esperando en la sala de espera
    cliente_listo.release() # Indicamos que el client esta listo para recortarse
    print(f"Cliente {id} se está pelando.")
    cliente_atendido.acquire() # El cliente espera a que lo atiendan
    if(clientes_en_espera>=1): # Si hay alguien esperando...
        print(f"{Fore.GREEN}Cliente {id} ha terminado, le avisa al siguiente que pase.{Style.RESET_ALL}")
        aviso.release() # El cliente le avisa al proximo que pase.
    else: # De lo contrario
        print(f"{Fore.BLUE}Cliente {id} ha terminado, el barbero se duerme porque no hay nadie. {Style.RESET_ALL}")
        barbero_durmiendo=True # El barbero se duerme
    


def barbero():
    global clientes_en_espera
    global barbero_durmiendo
    while True:
        if(barbero_durmiendo): # Si el barbero esta durmiendo
            entra_cliente.acquire() # Esperara a que alguien lo despierte
        barbero_listo.release() # Indicamos que el barbero ya esta listo
        cliente_listo.acquire() # Esperamos a que el cliente este listo para recortarse
        print("El barbero esta recortando a un cliente...") 
        time.sleep(random.randint(1, 2))  
        print("El barbero termino de recortar al cliente")
        cliente_atendido.release()  # Indicamos que terminamos de recortar al cliente

def main():
    hilos = []
    

    # Creamos el hilo del barbero
    barbero_hilo = threading.Thread(target=barbero)
    hilos.append(barbero_hilo)
    
    # Creamos los hilos de los clientes
    for i in range(num_clientes):
        t = threading.Thread(target=cliente, args=(i,))
        hilos.append(t)
    
    # Iniciamos todos los hilos
    for h in hilos:
        h.start()
    
    # Esperamos a que todos los hilos terminen
    for h in hilos:
        h.join()

main() # Iniciamos el programa