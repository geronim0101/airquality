import sqlite3


def get_sensor_data():
    # Simulate reading sensor data (replace with actual sensor readings)
    sensor_data = {
        'pm2': 2.0,
        'pm10': 4.5
    }
    return sensor_data


def insert_sensor_data(sensor_data):
    # Connect to SQLite database
    conn = sqlite3.connect('sensordb.db')
    cursor = conn.cursor()

    # Insert the air quality data into the database using the dictionary
    cursor.execute('''
    INSERT INTO read_data (created_at, pm2, pm10)
    VALUES (CURRENT_TIMESTAMP, :pm2, :pm10)
    ''', sensor_data)

    # Commit and close the connection
    conn.commit()
    conn.close()


# Example usage
sensor_data = get_sensor_data()
insert_sensor_data(sensor_data)
print("Sensor data has been inserted!")
