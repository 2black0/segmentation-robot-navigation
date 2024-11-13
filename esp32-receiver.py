import socket
import network
import time

# Replace with your WiFi credentials
SSID = "Your_SSID"
PASSWORD = "Your_PASSWORD"

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    print("\nWiFi connected!")
    print("IP address:", wlan.ifconfig()[0])

# Start a TCP server
def start_server():
    host = ''  # Listen on all available interfaces
    port = 8080

    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)  # Allow one client
    print(f"Server listening on port {port}...")

    while True:
        print("Waiting for a connection...")
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        try:
            while True:
                data = client_socket.recv(1024)  # Buffer size 1024 bytes
                if not data:
                    break
                print(f"Received: {data.decode('utf-8')}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            print("Closing connection...")
            client_socket.close()

if __name__ == "__main__":
    connect_wifi()
    start_server()
