import serial
import struct
import time
import sqlite3

# Set up the serial connection to the PMS5003 sensor
ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=2)

# Connect to (or create) the SQLite database
conn = sqlite3.connect('pm_data.db')
cursor = conn.cursor()

# Create a table to store PM sensor data if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pm_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        pm1_0_cf1 INTEGER,
        pm2_5_cf1 INTEGER,
        pm10_cf1 INTEGER,
        pm1_0_atm INTEGER,
        pm2_5_atm INTEGER,
        pm10_atm INTEGER
    )
''')
conn.commit()

# Function to store data in SQLite
def store_in_db(pm1_0_cf1, pm2_5_cf1, pm10_cf1, pm1_0_atm, pm2_5_atm, pm10_atm):
    cursor.execute('''
        INSERT INTO pm_readings (pm1_0_cf1, pm2_5_cf1, pm10_cf1, pm1_0_atm, pm2_5_atm, pm10_atm)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (pm1_0_cf1, pm2_5_cf1, pm10_cf1, pm1_0_atm, pm2_5_atm, pm10_atm))
    conn.commit()

# Function to read from the PMS5003 sensor
def read_pms5003():
    while True:
        if ser.in_waiting >= 32:  # Wait for at least 32 bytes to be available
            data = ser.read(32)   # Read 32 bytes from the serial connection
            if data[0] == 0x42 and data[1] == 0x4D:  # Check for the header bytes 0x42 and 0x4D
                frame_len = struct.unpack('>H', data[2:4])[0]  # Unpack frame length
                if frame_len == 28:  # Expected frame length is 28
                    values = struct.unpack('>HHHHHHHHHHHHHH', data[4:])  # Unpack the data
                    pm1_0_cf1 = values[0]
                    pm2_5_cf1 = values[1]
                    pm10_cf1 = values[2]
                    pm1_0_atm = values[3]
                    pm2_5_atm = values[4]
                    pm10_atm = values[5]
                    
                    # Print data to console
                    print(f"PM1.0 (CF=1): {pm1_0_cf1} µg/m³")
                    print(f"PM2.5 (CF=1): {pm2_5_cf1} µg/m³")
                    print(f"PM10  (CF=1): {pm10_cf1} µg/m³")
                    print(f"PM1.0 (ATM): {pm1_0_atm} µg/m³")
                    print(f"PM2.5 (ATM): {pm2_5_atm} µg/m³")
                    print(f"PM10  (ATM): {pm10_atm} µg/m³")
                    
                    # Store the data into the SQLite database
                    store_in_db(pm1_0_cf1, pm2_5_cf1, pm10_cf1, pm1_0_atm, pm2_5_atm, pm10_atm)
                    
                else:
                    print("Invalid frame length")
            else:
                print("Invalid data header")
        time.sleep(2)

# Run the program
try:
    read_pms5003()
except KeyboardInterrupt:
    ser.close()
    conn.close()  # Close the SQLite database connection when exiting
    print("Program stopped and database connection closed.")

