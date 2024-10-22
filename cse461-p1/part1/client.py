import socket
import sys

STEP = 1
ID = 738

def make_header(payload_len, psecret):
    header = bytes()
    header += payload_len.to_bytes(4, 'big')
    header += psecret.to_bytes(4, 'big')
    header += STEP.to_bytes(2, 'big')
    header += ID.to_bytes(2, 'big')
    return header

def print_header(header):
    payload_len = int.from_bytes(header[0:4], 'big')
    secret = int.from_bytes(header[4:8], 'big')
    step = int.from_bytes(header[8:10], 'big')
    student_id = int.from_bytes(header[10:12], 'big')
    print("payload_len", payload_len)
    print("prev secret", secret)
    print("step", step)
    print("id", student_id)

def part_a():
    # print("Beginning Secret A:")
    a_payload_len = 12
    a_psecret = 0
    a_header = make_header(a_payload_len, a_psecret)
    stage_a = 'hello world\0'
    stage_a_encoded_message = a_header + bytes(stage_a, 'utf-8')

    sock_a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4 and UDP
    sock_a.settimeout(3)
    try:
        sock_a.sendto(stage_a_encoded_message, (IP, UDP_PORT))
        response, addr1 = sock_a.recvfrom(28) # 12 bytes for header, 16 for payload
        num = int.from_bytes(response[12:16], 'big')
        b_len = int.from_bytes(response[16:20], 'big')
        port = int.from_bytes(response[20:24], 'big')
        secret_a = int.from_bytes(response[24:28], 'big')
        print("A:", secret_a)
        return num, b_len, port, secret_a
    finally:
        sock_a.close()


def part_b(num, b_len, udp_port, secret_a):
    # print("Beginning Secret B:")
    b_header = make_header(b_len + 4, secret_a) # packet_id + payload of length len
    sock_b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_b.settimeout(0.5)

    payload = bytearray(b_len)
    if len(payload) % 4 != 0:
        padding = bytearray(4 - len(payload) % 4)
        payload.extend(padding) # if not byte aligned add enough bytes for padding

    received = set()
    # print_header(b_header)
    try:
        for i in range(num):
            # print("packet ", i + 1)
            current_message = b_header + i.to_bytes(4,'big') + payload
            while i not in received:
                sock_b.sendto(current_message, (IP, udp_port))
                try:
                    curr_response, addr1 = sock_b.recvfrom(16)
                    acked_packet_id = int.from_bytes(curr_response[12:16], 'big')
                    if acked_packet_id == i:
                        received.add(acked_packet_id)
                        # print("packet", i, " received")
                except socket.timeout:
                    # print("Timed out on packet", i , " trying again")
                    continue
        # print("getting final payload")
        sock_b.settimeout(5)
        response = sock_b.recv(20)
        tcp_port = int.from_bytes(response[12:16], 'big')
        secret_b = int.from_bytes(response[16:20], 'big')
        print("B:", secret_b)
        return tcp_port
    finally:
        sock_b.close()


def part_c(tcp_port):
    # print("Beginning Secret C:")
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_tcp.connect((IP, tcp_port))
    sock_tcp.settimeout(3)

    try:
        response = sock_tcp.recv(28)
        num_2 = int.from_bytes(response[12:16], 'big')
        len_2 = int.from_bytes(response[16:20], 'big')
        secret_c = int.from_bytes(response[20:24], 'big')
        c = response[24:25]
        # print(num_2, len_2,secret_c, c)
        print("C:", secret_c)
        return num_2, len_2, c, secret_c, sock_tcp
    except:
        None

def part_d(num_2, len_2, c, secret_c, sock_tcp):
    try:
        # print("Beginning Secret D:")
        d_header = make_header(len_2, secret_c)
        d_payload = c * len_2
        if len(d_payload) % 4 != 0:
            d_padding = c * (4 - len(d_payload) % 4)
            d_payload += d_padding # if not byte aligned add enough bytes for padding
        d_message = d_header + d_payload

        for i in range(num_2):
            sock_tcp.send(d_message)
            # print(f"packet {i + 1}")
        sock_tcp.settimeout(10)
        response = sock_tcp.recv(16)
        secret_d = int.from_bytes(response[12:16], 'big')
        print("D:", secret_d)
    finally:
        sock_tcp.close()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Please provide specified arguments")
        sys.exit(1)
    IP = socket.gethostbyname(sys.argv[1])
    UDP_PORT = int(sys.argv[2])
    num, b_len, port, secret_a = part_a()
    tcp_port = part_b(num, b_len, port, secret_a)
    num_2, len_2, c, secret_c, sock_tcp = part_c(tcp_port)
    part_d(num_2, len_2, c, secret_c, sock_tcp)
    
