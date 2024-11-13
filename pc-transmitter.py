import socket
import time
import random

HOST = '192.168.100.48'  # IP address of your ESP32
PORT = 80                # Port number where the ESP32 server is listening

def send_data(data):
    """
    Sends data to the ESP32 server and prints the server's response.

    Parameters:
    data (bytes): The data to send to the server in bytes format.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(data)
            print("Data sent:", data)
            response = s.recv(1024)
            print("Received from server:", response.decode())
        except ConnectionError as e:
            print("Failed to connect or send data:", e)
        except Exception as e:
            print("An error occurred:", e)

# Generate 20 dummy data entries
def generate_dummy_data(count):
    dummy_data = []
    for _ in range(count):
        number1 = random.randint(100, 999)
        number2 = random.randint(100, 999)
        data_string = f"#{number1}${number2}".encode()  # Format as required and encode to bytes
        dummy_data.append(data_string)
    return dummy_data

# Example usage of the send_data function
if __name__ == "__main__":
    dummy_data_list = generate_dummy_data(20)
    for data in dummy_data_list:
        send_data(data)
        time.sleep(0.5)  # Delay of 1 second between sends