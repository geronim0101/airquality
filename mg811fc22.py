import time
import board
import digitalio
import busio
import sqlite3
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn

# Set up SPI
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)  # Chip select for MCP3008

# Create MCP3008 object
mcp = MCP3008(spi, cs)

# Select the channel connected to the MG811 (CH0 in this case)
chan = AnalogIn(mcp, MCP3008.P0)

def convert_to_voltage(adc_value):
    """ Convert ADC value to voltage (assuming 3.3V reference) """
    return (adc_value * 3.3) / 65535  # MCP3008 provides a 16-bit value

# Create (or connect to) the SQLite database and create a table if it doesn't exist
def setup_database():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    
    # Create table to store the ADC value and voltage
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adc_value INTEGER,
                    voltage REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    
    conn.commit()
    conn.close()

# Insert data into the SQLite database
def insert_data(adc_value, voltage):
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    
    # Insert the ADC value and voltage into the database
    c.execute('''INSERT INTO sensor_readings (adc_value, voltage) VALUES (?, ?)''', (adc_value, voltage))
    
    conn.commit()
    conn.close()

# Set up the database before starting
setup_database()

try:
    while True:
        # Read the sensor data from MCP3008
        adc_value = chan.value  # Raw ADC value
        voltage = chan.voltage  # Voltage value calculated automatically

        # Display the ADC value and the voltage
        print(f"ADC Value: {adc_value} Voltage: {voltage:.2f}V")

        # Insert the data into the database
        insert_data(adc_value, voltage)

        time.sleep(1)  # Delay for 1 second

except KeyboardInterrupt:
    print("Program stopped by User")
