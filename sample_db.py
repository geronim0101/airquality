import sqlite3


def read_dht11():
    humidity, temperature = 11, 10
    return humidity, temperature


def get_sensor_data():
    # Simulate reading sensor data (replace with actual sensor readings)
    h, t = read_dht11()

    sensor_data = {
        'pm2': 2.0,
        'pm10': 4.5,
        'humidity': h,
        'temperature': t

    }
    return sensor_data


def insert_sensor_data(sensor_data):
    # Connect to SQLite database
    conn = sqlite3.connect('sensordb.db')
    cursor = conn.cursor()

    # Insert the air quality data into the database using the dictionary
    cursor.execute('''
    INSERT INTO read_data (created_at, pm2, pm10, humidity, temperature)
    VALUES (CURRENT_TIMESTAMP, :pm2, :pm10, :humidity, :temperature)
    ''', sensor_data)

    # Commit and close the connection
    conn.commit()
    conn.close()


# Example usage
sensor_data = get_sensor_data()
insert_sensor_data(sensor_data)
print("Sensor data has been inserted!")
