import socket
import threading
import sys


nickname = input("Choose a nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 65432))

chat_is_connect = True


def receive():

    nickname_sent = False

    global chat_is_connect

    while chat_is_connect:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK' and not nickname_sent:
                client.send(nickname.encode('ascii'))
                nickname_sent = True

            elif message == 'EXIT':
                print("You have been disconnected from the chat.")
                chat_is_connect = False
                break
            else:
                print(message)

        except:
            print("An error occurred!")
            client.close()
            chat_is_connect = False
            break

    sys.exit()


def write():
    global chat_is_connect

    while chat_is_connect:
        try:
            message = input("")
            client.send(message.encode('ascii'))

        except:
            pass

    sys.exit()


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()