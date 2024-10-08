import sys 
import socket

UDP_IP = socket.gethostbyname('attu2.cs.washington.edu')
UDP_PORT = 41201

a_payload_len = 12
a_psecret = 0
step = 1
student_id = 81

a_header = bytes()
a_header += a_payload_len.to_bytes(4, 'big')
a_header += a_psecret.to_bytes(4, 'big')
a_header += step.to_bytes(2, 'big')
a_header += student_id.to_bytes(2, 'big')

stage_a = 'hello world\0'
stage_a_encoded_message = a_header + stage_a.encode('utf-8', 'strict')

sock_a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_a.settimeout(3)
try:
    sock_a.sendto(stage_a_encoded_message, (UDP_IP, UDP_PORT))
    response, _ = sock_a.recvfrom(16)
    b_num = int.from_bytes(response[0:4], 'big')
    b_len = int.from_bytes(response[4:8], 'big')
    b_port = int.from_bytes(response[8:12], 'big')
    secretA = int.from_bytes(response[12:16], 'big')
    print(b_num, b_len, b_port, secretA)
    print("stage a success, secretA is:", secretA)
finally:
    sock_a.close()


# b_payload_len = b_len + 4
# b_header = bytes()
# b_header += b_payload_len.to_bytes(4, 'big')
# b_header += secretA.to_bytes(4, 'big')
# b_header += step.to_bytes(2, 'big')
# b_header += student_id.to_bytes(2, 'big')

# sock_b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# try:
#     for i in range(b_num):
#         current_index = i
#         current_message = b_header + current_index.to_bytes(4,'big')
#         sock_b.sendto(current_message, (UDP_IP, b_port))
#         response, _ = sock_b.recvfrom(16)
#         print(response)
# finally:
#     sock_b.close()