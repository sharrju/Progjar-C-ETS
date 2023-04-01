import socket
import os
import multiprocessing
import threading
import ssl
from http import HttpServer

httpserver = HttpServer()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        rcv = ""
        while True:
            try:
                data = self.connection.recv(32)
                if data:
                    # merubah input dari socket (berupa bytes) ke dalam string
                    # agar bisa mendeteksi \r\n
                    d = data.decode()
                    rcv = rcv + d
                    if rcv[-2:] == '\r\n':
                        # end of command, proses string
                        hasil = httpserver.proses(rcv)
                        # hasil akan berupa bytes
                        # untuk bisa ditambahi dengan string, maka string harus di encode
                        hasil = hasil + "\r\n\r\n".encode()
                        # hasil sudah dalam bentuk bytes
                        self.connection.sendall(hasil)
                        rcv = ""
                        self.connection.close()
                else:
                    break
            except OSError as e:
                pass
        self.connection.close()

class Server(multiprocessing.Process):
    def __init__(self, hostname='testing.net'):
        self.the_clients = []
        self.hostname = hostname
        cert_location = os.getcwd() + '/certs/'
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile=cert_location + 'domain.crt',
                                     keyfile=cert_location + 'domain.key')
        multiprocessing.Process.__init__(self)

    def run(self):
        my_socket = self.context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_side=True)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.bind(('0.0.0.0', 8889))
        my_socket.listen(1)
        while True:
            self.connection, self.client_address = my_socket.accept()

            clt = ProcessTheClient(self.connection, self.client_address)
            clt.start()
            self.the_clients.append(clt)

def main():
    svr = Server()
    svr.start()

if __name__ == "__main__":
    main()