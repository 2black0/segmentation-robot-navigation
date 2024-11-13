import socket
import network

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

ssid = 'Wifi-Roboto'
password = 'arDY1234'
connect_to_wifi(ssid, password)
start_server()