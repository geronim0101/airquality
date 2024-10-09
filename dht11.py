import Adafruit_DHT
import time
import sqlite3

# Set sensor type and GPIO pin
sensor = Adafruit_DHT.DHT11
pin = 21

# Function to insert data into the database
def insert_data(temperature, humidity):
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()

    # Insert the sensor reading into the database
    c.execute('''INSERT INTO readings (temperature, humidity) VALUES (?, ?)''', (temperature, humidity))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Continuously read sensor data and save it to the database
while True:
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        # Insert the data into the database
        insert_data(temperature, humidity)
    else:
        print('Failed to get reading. Try again!')
    
    # Wait for a while before taking the next reading
    time.sleep(10)
