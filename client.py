import socket       # Para la conexión de red
import threading    # Para recibir y enviar mensajes al mismo tiempo
 
# ─────────────────────────────────────────────
# Configuración
# ─────────────────────────────────────────────
HOST = '127.0.0.1'    # IP del servidor — debe coincidir con server.py
PORT = 55556           # Puerto del servidor — debe coincidir con server.py
MAX_REINTENTOS = 3     # Cuántas veces intentamos conectarnos antes de rendirse
 
# ─────────────────────────────────────────────
# Pedir nombre de usuario antes de conectar
# ─────────────────────────────────────────────
username = input("Ingresá tu nombre de usuario: ")   # Le pedimos el nombre al usuario
 
# ─────────────────────────────────────────────
# Conexión con reintentos
# ─────────────────────────────────────────────
client = None   # Inicializamos la variable del socket como None
 
for intento in range(1, MAX_REINTENTOS + 1):           # Intentamos hasta MAX_REINTENTOS veces
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creamos el Socket | AF_INET = usamos IPv4 (ej: 192.168.x.x) | SOCK_STREAM = conexión TCP (confiable, con orden garantizado)
        client.connect((HOST, PORT))                                  # Intentamos conectarnos
        print(f"✅ Conectado al servidor {HOST}:{PORT}")              # Si llega acá, funcionó
        break                                                          # Salimos del loop de reintentos
 
    except ConnectionRefusedError:                                    # El servidor no está corriendo
        print(f"❌ Intento {intento}/{MAX_REINTENTOS}: servidor no disponible.")
        if intento == MAX_REINTENTOS:                                 # Si ya usamos todos los intentos
            print("No se pudo conectar. Verificá que el servidor esté corriendo.")
            exit(1)                                                    # Salimos del programa con error
 
# ─────────────────────────────────────────────
# Recibir mensajes — corre en su propio thread
# Mientras el usuario escribe, este thread escucha mensajes que llegan del servidor
# ─────────────────────────────────────────────
def recibir_mensajes():
    while True:
        try:
            mensaje = client.recv(1024).decode('utf-8')    # Esperamos mensaje del servidor
 
            if mensaje == "@username":                      # El servidor está pidiendo nuestro nombre
                client.send(username.encode('utf-8'))       # Lo enviamos
            else:
                print(mensaje)                             # Mostramos el mensaje en pantalla
 
        except ConnectionResetError:                       # El servidor se cayó o nos desconectó
            print("\n[Desconectado del servidor]")
            client.close()                                 # Cerramos el socket correctamente (bug corregido: faltaban los paréntesis)
            break
        except OSError:                                    # Error general de red
            break
 
# ─────────────────────────────────────────────
# Enviar mensajes — corre en el hilo principal
# Lee lo que el usuario escribe y lo manda al servidor
# ─────────────────────────────────────────────
def enviar_mensajes():
    while True:
        try:
            mensaje = input('')                            # Leemos lo que escribe el usuario
 
            if mensaje.strip() == "/exit":                # Si el usuario quiere salir
                client.send("/exit".encode('utf-8'))       # Avisamos al servidor
                print("Saliste del chat. ¡Hasta luego!")
                client.close()                             # Cerramos la conexión
                break                                      # Salimos del loop
 
            if mensaje.strip() == "/help":                # Si pide ayuda
                print("Comandos disponibles:")
                print("  /exit  → salir del chat")
                print("  /help  → mostrar esta ayuda")
                continue                                   # No enviamos nada al servidor, solo mostramos
 
            client.send(mensaje.encode('utf-8'))           # Enviamos el mensaje al servidor
 
        except OSError:                                    # Si el socket se cerró mientras escribía
            break
 
# ─────────────────────────────────────────────
# Arrancar los threads y el loop principal
# ─────────────────────────────────────────────
# Thread para recibir — corre en segundo plano
recibir_thread = threading.Thread(target=recibir_mensajes)
recibir_thread.daemon = True     # Si el programa principal termina, este thread termina también
recibir_thread.start()           # Arrancamos el thread de recepción
 
# El envío corre en el hilo principal (no en un thread separado)
enviar_mensajes()
 