import socket
import threading

class Client:
    def __init__(self, host='127.0.0.1', port=8080):
        self.server_host: str = host
        self.server_port: int = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_running = True

    def connect(self) -> None:
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            print(f"Connected to {self.server_host}:{self.server_port}")
        except ConnectionError:
            print("Failed to connect to the server.")
            self.is_running = False

    def send_message(self) -> None:
        while self.is_running:
            message = input() #"Enter message to send to the server (type 'exit' to quit): "
            if message.lower() == 'exit':
                self.is_running = False
                self.client_socket.close()
                break
            self.client_socket.sendall(message.encode())

    def receive_messages(self) -> None:
        while self.is_running:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    print(message)
                else:
                    self.is_running = False
                    print("Server connection closed.")
                    break
            except:
                print("Error receiving message from server.")
                self.is_running = False
                break

    def run(self) -> None:
        self.connect()
        if self.is_running:
            # Start a thread to listen for messages from the server
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

            # Main thread sends messages
            self.send_message()

            # Wait for the receive thread to finish
            receive_thread.join()

if __name__ == "__main__":
    client = Client()
    client.run()
