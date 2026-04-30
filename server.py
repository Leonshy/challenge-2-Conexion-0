import socket                          # Para crear conexiones de red
import threading                       # Para manejar múltiples clientes a la vez
from datetime import datetime          # Para agregar timestamps a los mensajes
 
# ─────────────────────────────────────────────
#  Configuración del servidor
# ─────────────────────────────────────────────
HOST = '127.0.0.1'   # IP local — solo funciona en esta misma máquina
PORT = 55556          # Puerto elegido arbitrariamente (debe coincidir con el cliente)
 
# ─────────────────────────────────────────────
#  Creación del socket del servidor
# ─────────────────────────────────────────────
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = usamos IPv4 | SOCK_STREAM = conexión TCP 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reusar el puerto si el servidor se reinicia rápido
server.bind((HOST, PORT))    # Le asignamos la dirección al socket
server.listen()               # Lo ponemos a escuchar conexiones entrantes
print(f"[SERVIDOR] Corriendo en {HOST}:{PORT}")  # Confirmamos que arrancó
 
# ─────────────────────────────────────────────
# Almacenamiento de clientes
# ─────────────────────────────────────────────
clientes = {}               # Diccionario: clave = socket del cliente, valor = su nombre de usuario
 
# ─────────────────────────────────────────────
#  Lock para acceso seguro al diccionario, solo un thread a la vez puede modificar clientes{}
# ─────────────────────────────────────────────
lock = threading.Lock()     
 
# ─────────────────────────────────────────────
#  Función para obtener timestamp actual
# ─────────────────────────────────────────────
def obtener_timestamp():
    return datetime.now().strftime("[%H:%M:%S]")  # Devuelve la hora actual en formato [HH:MM:SS]
 
# ─────────────────────────────────────────────
#  Broadcast — enviar mensaje a todos menos al emisor
# ─────────────────────────────────────────────
def broadcast(mensaje, emisor_socket):
    with lock:                                          # Bloqueamos el acceso al diccionario
        destinatarios = list(clientes.keys())           # Copiamos la lista para iterar seguro
 
    for cliente in destinatarios:                       # Recorremos todos los clientes
        if cliente != emisor_socket:                    # Nos saltamos al que mandó el mensaje
            try:
                cliente.send(mensaje)                   # Enviamos el mensaje
            except OSError:                             # Si el socket ya está muerto
                eliminar_cliente(cliente)               # Lo eliminamos limpiamente
 
# ─────────────────────────────────────────────
#  Eliminar cliente — centraliza la baja de un cliente
# ─────────────────────────────────────────────
def eliminar_cliente(cliente_socket):
    with lock:                                              # Bloqueamos el diccionario
        if cliente_socket in clientes:                      # Verificamos que exista
            username = clientes.pop(cliente_socket)         # Lo eliminamos y guardamos su nombre
            try:
                cliente_socket.close()                      # Cerramos la conexión
            except OSError:                                 # Si ya estaba cerrado, ignoramos
                pass
    return username                                         # Devolvemos el nombre para avisar a los demás
 
# ─────────────────────────────────────────────
#  Manejar mensajes de un cliente — corre en su propio hilo
# Cada cliente conectado tiene su propio hilo ejecutando esta función
# ─────────────────────────────────────────────
def manejar_cliente(cliente_socket):
    while True:
        try:
            mensaje = cliente_socket.recv(1024).decode('utf-8')   # Esperamos un mensaje (máx 1024 bytes)
 
            if not mensaje:                                        # Si el mensaje está vacío, el cliente se desconectó
                break
 
            if mensaje.strip() == "/exit":                        # Si el cliente mandó el comando /exit
                break                                              # Salimos del loop limpiamente
 
            # Armamos el mensaje con timestamp para todos los demás
            with lock:
                username = clientes.get(cliente_socket, "Desconocido")  # Obtenemos el nombre del cliente
 
            timestamp = obtener_timestamp()                        # Generamos el timestamp
            mensaje_formateado = f"{timestamp} {username}: {mensaje}".encode('utf-8')  # Armamos el mensaje final
            broadcast(mensaje_formateado, cliente_socket)          # Lo enviamos a todos
 
        except ConnectionResetError:       # El cliente cerró la conexión abruptamente (ej: cerró la terminal)
            break
        except OSError:                    # Error general de red
            break
 
    # Cuando salimos del loop, limpiamos al cliente
    username = eliminar_cliente(cliente_socket)
    mensaje_salida = f"{obtener_timestamp()} ChatBot: {username} salió del chat.".encode('utf-8')
    broadcast(mensaje_salida, cliente_socket)   # Avisamos a todos que se fue
    print(f"[SERVIDOR] {username} se desconectó.")  # Log en la consola del servidor
 
# ─────────────────────────────────────────────
#  Aceptar conexiones — loop principal del servidor
# ─────────────────────────────────────────────
def aceptar_conexiones():
    while True:
        try:
            cliente_socket, direccion = server.accept()              # Esperamos que alguien se conecte (bloqueante)
 
            cliente_socket.send("@username".encode('utf-8'))         # Le pedimos el nombre de usuario
            username = cliente_socket.recv(1024).decode('utf-8')     # Recibimos el nombre
 
            with lock:                                               # Bloqueamos antes de modificar el diccionario
                clientes[cliente_socket] = username                  # Guardamos socket → nombre
 
            print(f"[SERVIDOR] {username} conectado desde {direccion}")  # Log en servidor
 
            mensaje_bienvenida = f"{obtener_timestamp()} ChatBot: {username} entró al chat!".encode('utf-8')
            broadcast(mensaje_bienvenida, cliente_socket)            # Avisamos a todos que entró
 
            cliente_socket.send("Conectado al servidor. Escribí /exit para salir.\n".encode('utf-8'))  # Confirmamos al cliente
 
            # Creamos y arrancamos un hilo exclusivo para este cliente
            thread = threading.Thread(target=manejar_cliente, args=(cliente_socket,))
            thread.daemon = True    # Si el servidor muere, el hilo muere con él
            thread.start()
 
        except OSError:             # Si el servidor se cierra, salimos del loop
            break
 
# ─────────────────────────────────────────────
#  Aca empezamos 
# ─────────────────────────────────────────────
aceptar_conexiones()   # Arrancamos el servidor