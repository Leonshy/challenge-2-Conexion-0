📡 Chat en Tiempo Real — Challenge 2
Un sistema de chat por terminal construido desde cero con sockets TCP y threads en Python. Sin frameworks. Sin magia. Solo red y código.

🚀 Cómo ejecutar
Paso 1 — Arrancá el servidor (en una terminal):
bashpython server.py
Paso 2 — Conectá uno o más clientes (cada uno en su propia terminal):
bashpython client.py
No requiere dependencias externas. Solo Python 3.10 o superior.

💬 Comandos disponibles
ComandoAcción/exitSalir del chat limpiamente/helpVer los comandos disponibles

🏗️ Arquitectura
servidor (server.py)
│
├── Espera conexiones en loop infinito
├── Por cada cliente nuevo → crea un thread dedicado
├── Recibe mensajes → hace broadcast a todos los demás
└── Maneja desconexiones sin caerse

cliente (client.py)
│
├── Intenta conectarse (hasta 3 reintentos)
├── Thread de recepción → muestra mensajes que llegan
└── Loop principal → envía lo que el usuario escribe

🔧 Decisiones técnicas
Diccionario en lugar de listas paralelas
El código original usaba clients[] y usernames[] sincronizadas por índice. Si un cliente se desconectaba en el momento justo, podían desincronizarse. Lo reemplazamos por un diccionario {socket: username} que es atómico por naturaleza.
Threading.Lock()
Varios threads acceden al diccionario de clientes al mismo tiempo. Sin un Lock, dos threads podrían modificarlo simultáneamente y corromperlo. El Lock garantiza que solo un thread a la vez puede tocar la lista.
Excepciones específicas
El original usaba except: desnudo, que captura hasta errores de sistema. Usamos ConnectionResetError y OSError para saber exactamente qué falló.
Reintentos en el cliente
Si el servidor no está disponible, el cliente reintenta hasta 3 veces antes de rendirse, en lugar de crashear al instante.
Timestamps
Cada mensaje muestra la hora en formato [HH:MM:SS] para saber cuándo se dijo qué.

❓ Las preguntas del challenge
¿Quién sos después de este reto?
Alguien que entiende que detrás de cada app de chat hay un socket esperando en un loop infinito, un thread por cada persona conectada, y un broadcast que replica cada mensaje a todos los demás. La magia desapareció, quedó el protocolo.
¿Cómo sobrevivió tu aplicación?
Con un Lock que protege el estado compartido, excepciones específicas que no dejan pasar errores silenciosos, y una función centralizada para eliminar clientes que garantiza que ningún socket quede zombie.
¿Qué aprendiste cuando todo se rompió?
Que client.close sin paréntesis no cierra nada. Que dos listas paralelas son una bomba de tiempo. Que un except: desnudo es peor que no manejar el error, porque esconde lo que realmente falló.