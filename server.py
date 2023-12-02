import threading
import socket
import sqlite3
import datetime

db_lock = threading.Lock()


# Создание таблицы сообщений, если она не существует
# c.execute('''CREATE TABLE IF NOT EXISTS messages
#              (id INTEGER PRIMARY KEY AUTOINCREMENT,
#               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#               nickname TEXT,
#               message TEXT)''')


# Функция для сохранения сообщений в базе данных
def save_message(nickname, message):
    with db_lock:
        conn = sqlite3.connect('chat.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO messages (nickname, message) VALUES (?, ?)", (nickname, message))
            conn.commit()
        except sqlite3.OperationalError:
            print("Ошибка сохранения сообщения в базе данных.")

        conn.close()


# Функция для получения истории сообщений из базы данных
def get_message_history():
    with db_lock:
        conn = sqlite3.connect('chat.db')
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM messages")
            messages = c.fetchall()
            message_history = '\n'.join(
                f'{message[1]} <{message[2]}> {message[3]}' for message in messages)
            conn.close()
            return message_history or "Нет сообщений"

        except sqlite3.OperationalError:
            print("Ошибка получения истории сообщений из базы данных.")
            conn.close()
            return ""


host = '127.0.0.1'  # Standard loopback interface address (localhost)
port = 65432  # Port to listen on (non-privileged ports are > 1023)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('ascii').strip()

            index = clients.index(client)
            nickname = nicknames[index]

            if message != "":

                if "/exit" == message:

                    client.send("EXIT".encode('ascii'))

                    clients.remove(client)
                    client.close()

                    nicknames.remove(nickname)

                    broadcast(f'{nickname} left!'.encode('ascii'))
                    break

                else:
                    broadcast(
                        f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} <{nickname}> {message}'
                        .encode('ascii'))
                    save_message(nickname, message)

        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()

            nickname = nicknames[index]
            broadcast(f'{nickname} left!'.encode('ascii'))
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('ascii'))
        clients.append(client)

        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)

        print(f"Nickname is {nickname}")

        client.send('Connected to server!'.encode('ascii'))
        client.send(f'Current message history:\n{get_message_history()}'.encode('ascii'))

        broadcast(f'{nickname} joined! \n'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server is listening...")
receive()
