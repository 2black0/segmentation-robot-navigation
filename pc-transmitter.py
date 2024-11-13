import socket

# ESP32 IP and Port (use the IP shown in the ESP32 Serial Monitor)
ESP32_IP = '192.168.1.100'  # Replace with your ESP32's IP
ESP32_PORT = 8080           # Port defined in the ESP32 code

# Create a socket and connect to ESP32
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ESP32_IP, ESP32_PORT))

try:
    while True:
        message = input("Enter message to send (type 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        client_socket.sendall(message.encode())
        print(f"Sent: {message}")
finally:
    client_socket.close()
    print("Connection closed.")
