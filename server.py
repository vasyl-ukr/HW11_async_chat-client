import socket
import threading

CONNECTIONS = set()

class SockThread(threading.Thread):
    def __init__(self, conn, *a, **kwa):
        self.conn = conn
        super().__init__(*a, **kwa)

    def run(self):
        with self.conn:
            while True:
                data = self.conn.recv(1024)
                print('Recieved message:', data)
                if not data:
                    print(f'Client {self.conn} disconnected!')
                    CONNECTIONS.remove(self.conn)
                    break
                for conn in CONNECTIONS:
                    conn.sendall(data)

def main():
    with socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM,
                       proto=socket.IPPROTO_TCP) as sock:
        sock.bind(('0.0.0.0', 8887))
        sock.listen()

        while True:
            conn, addr = sock.accept()
            CONNECTIONS.add(conn)
            print(f'Client {addr} connected.')
            sock_thread = SockThread(conn)
            sock_thread.start()

if __name__ == '__main__':
    main()
