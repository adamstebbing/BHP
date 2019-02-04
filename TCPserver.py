import socket
import threading

ip = "127.0.0.1"
port = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((ip, port))
s.listen(5)

print "Listening on %s: %d" % (bind_ip, v\bind_port)

def handle_client(client_socket):
    request = client_socket.recv(1024)

    print "Recieved: %s" % request

    client_socket.send("ACK!")

    client_socket.close()

while True:
    client, addr = s.accept()

    print "Accepted connection from: %s: %d" % (addr[0], addr[1])

    client_thread = threading.Thread(target=handle_client, args=(client,))
    client_thread.start()

