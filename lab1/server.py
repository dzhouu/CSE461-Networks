
import socket
import sys
import threading
from struct import pack, unpack
import random

if len(sys.argv) != 3:
    print("Please provide specified arguments")
    sys.exit(1)

CLIENT_TIMEOUT = 3


def make_header(payload_len, step, id, psecret):
    header = bytes()
    header += payload_len.to_bytes(4, 'big')
    header += psecret.to_bytes(4, 'big')
    header += step.to_bytes(2, 'big')
    header += id.to_bytes(2, 'big')
    return header

"""
Parameters:
header: must be a 12-byte object
"""
def read_header(header):
    payload_len = int.from_bytes(header[0:4], 'big')
    secret = int.from_bytes(header[4:8], 'big')
    step = int.from_bytes(header[8:10], 'big')
    student_id = int.from_bytes(header[10:12], 'big')
    return (payload_len, secret, step, student_id)

""
def verify_header(header, exp_secret, exp_step, exp_id):
    _, header_secret, header_step, header_id = read_header(header)
    return (header_secret == exp_secret and header_step == exp_step and header_id == exp_id)

def handle_new_connection(socket, student_id):
    socket.settimeout(CLIENT_TIMEOUT)
    
    # Part a
    try:
        # Check for correct header 
        header = socket.recv(12)
        if len(header) != 12:
            print("I think this checks for the first 12 bytes for header?")
            return

        payload_len, secret, step, student_id, payload = read_header(header)

        if not verify_header(header, 0, 1, student_id):
            print("failed header check")
            return

        payload = socket.recv(payload_len)
        if payload.decode('utf-8') != "hello world":
            print("bad payload")
            return

        # Make random data for part A response
        a_num, a_len, a_udp_port, secretA = random.randint(7, 20), random.randint(20, 100), random.randint(10000, 65535), random.randint(100, 999)

        response_header = make_header(len(response_payload), 0, 2, student_id)
        response_payload = bytes()
        socket.send(response_header + response_payload)

    except:
        pass


def start_server(server_ip, port, student_id):
    # Starts up a server listening for incoming client connections
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((server_ip, port))
    server.listen(5)

    while True:
        try:
            client_socket, client_address = server.accept()
            try:
                # If new client tries to connect to us then create a new thread (i have absolutely no idea how this works ngl i just did geeksforgeeks)
                # TODO: CLOSE THE THREAD WHEN DONE WITH IT
                thread = threading.Thread(target=handle_new_connection, args=(client_socket, student_id))
                thread.start()
            finally:
                client_socket.close()
        finally:
            server.close()


# Run this to star the server
server_ip = "attu2.cs.washington.edu"
port = 31415
id = 783
start_server(server_ip, port, id)
