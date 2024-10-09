import time
import board
import digitalio
import busio
import sqlite3
import Adafruit_DHT
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn

# Set up DHT11 sensor
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 21

# Set up SPI for MCP3008
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)  # Chip select for MCP3008

# Create MCP3008 object
mcp = MCP3008(spi, cs)

# Select the channel connected to the MG811 (CH0 in this case)
chan = AnalogIn(mcp, MCP3008.P0)

# Create (or connect to) the SQLite database and create a table if it doesn't exist
def setup_database():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    
    # Create table to store sensor readings
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    temperature REAL,
                    humidity REAL,
                    adc_value INTEGER,
                    voltage REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    
    conn.commit()
    conn.close()

# Insert data into the SQLite database
def insert_data(temperature, humidity, adc_value, voltage):
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    
    # Insert the DHT11 and MCP3008 sensor readings into the database
    c.execute('''INSERT INTO sensor_readings (temperature, humidity, adc_value, voltage)
                 VALUES (?, ?, ?, ?)''', (temperature, humidity, adc_value, voltage))
    
    conn.commit()
    conn.close()

# Set up the database before starting
setup_database()

try:
    while True:
        # Read temperature and humidity from DHT11 sensor
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        # Read the sensor data from MCP3008 (voltage sensor)
        adc_value = chan.value  # Raw ADC value
        voltage = chan.voltage  # Voltage value calculated automatically

        # If DHT11 reading is valid, display and log the data
        if humidity is not None and temperature is not None:
            print(f'Temp={temperature:.1f}*C  Humidity={humidity:.1f}%')
        else:
            print('Failed to get DHT11 reading. Try again!')

        # Display the MCP3008 readings
        print(f"ADC Value: {adc_value} Voltage: {voltage:.2f}V")

        # Insert the sensor readings into the database
        insert_data(temperature, humidity, adc_value, voltage)

        # Wait for a second before the next reading
        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped by User")

