import socket
import sys
import threading
import random
import string

CLIENT_TIMEOUT = 3
student_id = 0
SERVER_IP = socket.gethostbyname(sys.argv[1])

"""
Returns the header given all the data to make the header
"""
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

Returns:
(payload_len, secret, step, student_id): parsed header data
"""
def read_header(header):
    payload_len = int.from_bytes(header[0:4], 'big')
    secret = int.from_bytes(header[4:8], 'big')
    step = int.from_bytes(header[8:10], 'big')
    student_id = int.from_bytes(header[10:12], 'big')
    return payload_len, secret, step, student_id

"""
Returns:
true if all data in the header matches the expected data, otherwise false
"""
def verify_header(header, exp_len, exp_secret, exp_step, exp_id):
    header_payload_len, header_secret, header_step, header_id = read_header(header)
    return header_payload_len == exp_len and header_secret == exp_secret and header_step == exp_step and header_id == exp_id

"""
Parameters:
data: list of (data, num_bytes) to package into a payload

Returns:
payload (bytes): payload that is padded to a 4-byte boundary
"""
def package_payload(data_list):
    payload = bytes()
    for data, num_bytes in data_list:
        payload += data.to_bytes(num_bytes, 'big')
    
    payload += b'\00' * (0 if len(payload) % 4 == 0 else 4 - (len(payload) % 4)) # pad the payload to 4-byte boundary iff not already on the boundary
    return payload

"""
Parameters:
secret: secret of previous step

Returns:
True: if secret is not equal to -1 (No Errors)
False: if secret is equal to -1 (Error Occurred)
"""
def check_secret(secret):
    if secret == -1:
        return True
    return False


def part_a(server: socket, data, client_address):
    try:
        # Parse client data
        header = data[:12]
        if len(header) != 12:
            print("Bad header")
            raise ValueError

        payload = data[12:]

        # Check for correct header
        if not verify_header(header, 12, 0, 1, student_id): # Client should give psecret 0 and step 1 for it's part A message
            print("failed header check")
            raise ValueError
        
        # Check for correct payload
        if payload.decode('utf-8') != "hello world\x00":
            print("bad payload")
            raise ValueError

        # Make random data for part A response
        a_num = random.randint(7, 20)
        a_len = random.randint(20, 100)
        a_udp_port = random.randint(10000, 65535)
        secret_a = random.randint(100, 999)

        # Create response packet
        response_payload = package_payload([(a_num, 4), (a_len, 4), (a_udp_port, 4), (secret_a, 4)])
        response_header = make_header(len(response_payload), 2, student_id, 0)
        
        # server.settimeout(CLIENT_TIMEOUT)
        server.sendto(response_header + response_payload, client_address)
        return a_num, a_len, a_udp_port, secret_a
    except ValueError:
        return -1, -1, -1, -1
    
def part_b(a_num, a_len, a_udp_port, secret_a):
    # Create a new server to listen for the client's part b response
    part_b_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        part_b_server.bind((SERVER_IP, a_udp_port))
    except:
        print(f"Port {port} is already in use")
        part_b_server.close()
        return -1 -1

    part_b_server.settimeout(CLIENT_TIMEOUT)
    expected_payload_len = 4 + a_len + (0 if a_len % 4 == 0 else 4 - (a_len % 4))
    b_tcp_port = random.randint(1024, 49151)
    secret_b = random.randint(100,999)

    try:
        # Receive a_num packets to the client
        for packet_num in range(a_num):
            b_data, client_address = part_b_server.recvfrom(1024)

            # Parse data
            header = b_data[:12]
            if len(header) != 12:
                print("Bad header")
                part_b_server.close()
                raise ValueError

            payload = b_data[12:]

            # Check for correct header
            if not verify_header(header, a_len + 4, secret_a, 1, student_id):
                print("Failed header check")
                part_b_server.close()
                raise ValueError
            
            packet_id = payload[:4]

            # Check for correct payload
            if len(payload) != expected_payload_len or payload[4:].decode('utf-8') != "\x00" * (expected_payload_len - 4):
                print("Bad payload")
                part_b_server.close()
                raise ValueError
            
            response_payload = package_payload([(int.from_bytes(packet_id, 'big'), 4)])
            response_header = make_header(len(response_payload), 1, student_id, secret_a)
            part_b_server.sendto(response_header + response_payload, client_address)
    except ValueError:
        part_b_server.close()
        return -1, -1
    else:
        # Create the payload header and payload that will be sent by the server
        final_payload = package_payload([(b_tcp_port, 4), (secret_b, 4)])
        final_header = make_header(len(final_payload), 1, student_id, secret_a)
        part_b_server.sendto(final_header + final_payload, client_address)
        part_b_server.close()
        return secret_b, b_tcp_port

def part_c(tcp_port, secret_b):
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_server.bind((SERVER_IP, tcp_port))
    except:
        print(f"Port {port} is already in use")
        tcp_server.close()
        return

    tcp_server.settimeout(CLIENT_TIMEOUT)
    tcp_server.listen(1 + 20)
    connection, client_address = tcp_server.accept()
    try:
        num2 = random.randint(7, 20)
        len2 = random.randint(20, 100)
        secret_c = random.randint(100, 999)
        string.ascii_letters
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        c = random.choice(string.ascii_letters)
        response_header = make_header(25, 2, student_id, secret_b)
        response_payload = package_payload([(num2, 4), (len2, 4), (secret_c, 4), (ord(c), 1)])
        connection.sendto(response_header + response_payload, client_address)
        return num2, len2, c, secret_c, tcp_server, connection, client_address
    except:
        None

def part_d(num2, len2, c, secret_c, tcp_server, connection, client_address):
    try:
        expected_payload_len = len2 + (0 if len2 % 4 == 0 else 4 - (len2 % 4))
        while num2 > 0:
            response = connection.recv(12 + expected_payload_len)

            # Parse data
            header = response[:12]
            if len(header) != 12:
                print("Bad header")
                return

            payload = response[12:]

            # Check for correct header
            if not verify_header(header, len2, secret_c, 1,
                                 student_id):
                print("Failed header check")
                tcp_server.close()
                return

            # Check for correct payload of char c
            if len(payload) != expected_payload_len:
                print("Bad payload: Bad payload length")
                tcp_server.close()
                return

            # Need to Check each entry in the pay-load
            # the pay-load should be in Unicode of char c from ord() in client side
            for char in range(len2):
                if chr(payload[char]) != c:
                    print(f"Bad payload: Unexpected char:", {chr(payload[char])})
                    tcp_server.close()
                    return

            num2 -= 1
        secret_d = random.randint(100, 999)
        response_payload = package_payload([(secret_d, 4)])
        response_header = make_header(len(response_payload), 1, student_id, secret_c)
        connection.sendto(response_header + response_payload, client_address)
        return secret_d
    finally:
        tcp_server.close()


def handle_new_connection(server, data, client_address, stop_event):
    global student_id
    student_id = int.from_bytes(data[10:12], 'big')
    if stop_event.is_set():
        return
    a_num, a_len, a_udp_port, secret_a = part_a(server, data, client_address)
    if check_secret(secret_a):
        return
    secret_b, tcp_port= part_b(a_num, a_len, a_udp_port, secret_a)
    if check_secret(secret_b):
        return
    num2, len2, c, secret_c, tcp_server, connection, client_address = part_c(tcp_port, secret_b)
    secret_d = part_d(num2, len2, c, secret_c, tcp_server, connection, client_address)
    print(f"secret A is {secret_a}")
    print(f"secret B is {secret_b}")
    print(f"secret C is {secret_c}")
    print(f"secret D is {secret_d}")


def start_server(port):
    # Starts up a server listening for incoming client connections
    stop_event = threading.Event()
    threads = []
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.bind((SERVER_IP, port))
    except:
        print(f"Port {port} is already in use")
        server.close()
        return

    try:
        while True:
            data, client_address = server.recvfrom(1024)
            try:
                thread = threading.Thread(target=handle_new_connection, args=(server, data, client_address, stop_event))
                thread.start()
                threads.append(thread)
            except Exception as e:
                print(e)

    except KeyboardInterrupt:
        server.close()
        print("\n Ctrl + C, Exiting")
    finally:
        stop_event.set()  # Signal all threads to stop
        for thread in threads:
            thread.join()  # Wait for all threads to finish
        server.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Please provide specified arguments")
        sys.exit(1)
    port = int(sys.argv[2])
    start_server(port)

