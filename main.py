import time
import board
import digitalio
import busio
import sqlite3
import Adafruit_DHT
import serial
import struct
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn

# Set up DHT11 sensor
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 21

# Set up SPI for MCP3008 (for MG811 sensor)
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)  # Chip select for MCP3008
mcp = MCP3008(spi, cs)

# Select the channel connected to the MG811 (CH0 in this case)
chan = AnalogIn(mcp, MCP3008.P0)

# Set up the serial connection to the PMS5003 sensor
ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=2)

# Create (or connect to) the SQLite database and create tables if they don't exist
def setup_database():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()

    # Create table for DHT11 and MG811 sensor readings
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    temperature REAL,
                    humidity REAL,
                    adc_value INTEGER,
                    voltage REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')

    # Create table for PM sensor readings
    c.execute('''CREATE TABLE IF NOT EXISTS pm_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pm1_0_cf1 INTEGER,
                    pm2_5_cf1 INTEGER,
                    pm10_cf1 INTEGER,
                    pm1_0_atm INTEGER,
                    pm2_5_atm INTEGER,
                    pm10_atm INTEGER
                )''')

    conn.commit()
    conn.close()

# Insert DHT11 and MG811 data into the SQLite database
def insert_data(temperature, humidity, adc_value, voltage):
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute('''INSERT INTO sensor_readings (temperature, humidity, adc_value, voltage)
                 VALUES (?, ?, ?, ?)''', (temperature, humidity, adc_value, voltage))
    conn.commit()
    conn.close()

# Insert PMS5003 data into the SQLite database
def store_pm_data(pm1_0_cf1, pm2_5_cf1, pm10_cf1, pm1_0_atm, pm2_5_atm, pm10_atm):
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute('''INSERT INTO pm_readings (pm1_0_cf1, pm2_5_cf1, pm10_cf1, pm1_0_atm, pm2_5_atm, pm10_atm)
                 VALUES (?, ?, ?, ?, ?, ?)''', (pm1_0_cf1, pm2_5_cf1, pm10_cf1, pm1_0_atm, pm2_5_atm, pm10_atm))
    conn.commit()
    conn.close()

# Function to read from PMS5003 sensor
def read_pms5003():
    if ser.in_waiting >= 32:  # Wait for at least 32 bytes to be available
        data = ser.read(32)   # Read 32 bytes from the serial connection
        if data[0] == 0x42 and data[1] == 0x4D:  # Check for the header bytes 0x42 and 0x4D
            frame_len = struct.unpack('>H', data[2:4])[0]
            if frame_len == 28:  # Expected frame length is 28
                values = struct.unpack('>HHHHHHHHHHHHHH', data[4:])
                pm1_0_cf1 = values[0]
                pm2_5_cf1 = values[1]
                pm10_cf1 = values[2]
                pm1_0_atm = values[3]
                pm2_5_atm = values[4]
                pm10_atm = values[5]
                print(f"PM1.0 (CF=1): {pm1_0_cf1} µg/m³, PM2.5 (CF=1): {pm2_5_cf1} µg/m³, PM10 (CF=1): {pm10_cf1} µg/m³")
                print(f"PM1.0 (ATM): {pm1_0_atm} µg/m³, PM2.5 (ATM): {pm2_5_atm} µg/m³, PM10 (ATM): {pm10_atm} µg/m³")

                # Store the PM sensor data into the database
                store_pm_data(pm1_0_cf1, pm2_5_cf1, pm10_cf1, pm1_0_atm, pm2_5_atm, pm10_atm)
            else:
                print("Invalid frame length")
        else:
            print("Invalid data header")

# Set up the database before starting
setup_database()

try:
    while True:
        # Read temperature and humidity from DHT11 sensor
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        # Read the sensor data from MCP3008 (MG811 sensor)
        adc_value = chan.value  # Raw ADC value
        voltage = chan.voltage  # Voltage value calculated automatically

        # If DHT11 reading is valid, display and log the data
        if humidity is not None and temperature is not None:
            print(f'Temperature: {temperature:.1f}°C  Humidity: {humidity:.1f}%')
        else:
            print('Failed to get DHT11 reading.')

        # Display the MCP3008 readings (for MG811 CO2 sensor)
        print(f"CO2 Sensor (MG811) ADC Value: {adc_value} Voltage: {voltage:.2f}V")

        # Insert the DHT11 and MG811 data into the database
        insert_data(temperature, humidity, adc_value, voltage)

        # Read and log PMS5003 sensor data
        read_pms5003()

        # Wait for a second before the next reading
        time.sleep(1)

except KeyboardInterrupt:
    ser.close()
    print("Program stopped by User.")
