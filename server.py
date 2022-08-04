import socket
import threading

HOST = '0.0.0.0'
PORT = 5355

THREADS = []


class ClientProcesingThread(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__()
        self.conn = conn
        self.addr = addr

    def run(self):
        with self.conn:
            global THREADS
            print('Connected by', self.addr)
            while True:
                data = self.conn.recv(1024)

                print(f'Recieved message {data} from {self.addr}')

                if not data:
                    THREADS = [t for t in THREADS if t != self]
                    break

                for thread in THREADS:
                    if thread == self:
                        continue
                    else:
                        thread.conn.sendall(data)


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            conn_thread = ClientProcesingThread(conn, addr)
            THREADS.append(conn_thread)
            conn_thread.start()
