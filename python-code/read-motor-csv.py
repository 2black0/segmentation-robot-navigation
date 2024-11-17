import csv

# Nama file CSV
CSV_FILE = "motor_data.csv"

def read_csv(file_name):
    try:
        with open(file_name, mode="r") as file:
            reader = csv.DictReader(file)
            print(f"Reading data from {file_name}:\n")
            
            # Menampilkan header
            print("\t".join(reader.fieldnames))
            
            # Menampilkan isi file
            for row in reader:
                print(f"{row['Timestamp']}\t{row['TurnValue']}\t{row['ThrottleValue']}\t{row['SafetyValue']}\t{row['ModeValue']}\t{row['ForwardValue']}\t{row['StatusValue']}")
    except FileNotFoundError:
        print(f"Error: File {file_name} not found.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

# Memanggil fungsi untuk membaca CSV
read_csv(CSV_FILE)