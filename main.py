import socket
import network
from ota import OTAUpdater

SSID = 'POCOF5'
PASSWORD = '1234567890'
#firmware_url = "https://raw.githubusercontent.com/2black0/ota-esp32/"
firmware_url = "https://github.com/2black0/segmentation-robot-navigation"

ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "main.mpy")
ota_updater.download_and_install_update_if_available()

def connect_to_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)

    while not station.isconnected():
        pass

    print('Connection successful')
    print(station.ifconfig())

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(1)
    
    #print('Waiting for connections...')
    while True:
        conn, addr = s.accept()
        #print('Connected by', addr)
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data_string = data.decode('utf-8')  # Convert bytes to string
                #print('Received:', data_string)
                # Parsing the data
                if data_string.startswith('#') and '$' in data_string:
                    parts = data_string[1:].split('$')  # Remove '#' and split at '$'
                    if len(parts) == 2:
                        data1 = int(parts[0])
                        data2 = int(parts[1])
                        print('Data1:', data1, 'Data2:', data2)
                conn.send(b'ACK')  # Send acknowledgment after processing
        except Exception as e:
            print('Error:', str(e))
        finally:
            conn.close()
            #print('Connection closed, waiting for next connection...')

connect_to_wifi(SSID, PASSWORD)
start_server()
