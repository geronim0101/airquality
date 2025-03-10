import requests
from datetime import datetime

# Define the API endpoint
API_URL = "https://bantayhangin.pythonanywhere.com/api/query/"

# Function to check or insert a Location instance


def ensure_location_exists():
    query_check = "SELECT id FROM airquality_location WHERE id = 1;"
    query_insert = """
    INSERT INTO airquality_location (id, loc_description, latitude, longitude)
    VALUES (1, 'Default Location', 14.5995, 120.9842);
    """

    # Check if Location exists
    response_check = requests.get(API_URL, params={'query': query_check})
    if response_check.status_code == 200:
        data = response_check.json().get('data', [])
        if data:
            print("Location instance with ID 1 exists.")
            return 1
        else:
            # Insert Location
            response_insert = requests.post(
                API_URL, data={'query': query_insert})
            if response_insert.status_code == 200:
                print("Location instance with ID 1 created.")
                return 1
            else:
                raise Exception(
                    f"Failed to create Location instance: {response_insert.json()}")
    else:
        raise Exception(
            f"Failed to query Location table: {response_check.json()}")

# Construct the INSERT query


def build_insert_query(reading_loc):
    temperature = 25.5
    humidity = 60.0
    CO2 = 400.0
    PM25 = 15.0
    PM10 = 10.0
    TVOC = 0.1
    HCHO = 0.05
    reading_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    query = f"""
    INSERT INTO airquality_sensor 
    (temperature, humidity, CO2, PM25, PM10, TVOC, HCHO, reading_loc_id, reading_date) 
    VALUES 
    ({temperature}, {humidity}, {CO2}, {PM25}, {PM10}, {TVOC}, {HCHO}, {reading_loc}, '{reading_date}');
    """
    return query

# Function to insert sensor data


def insert_sensor_data():
    try:
        # Ensure Location exists
        reading_loc = ensure_location_exists()

        # Build and execute the INSERT query
        query = build_insert_query(reading_loc)
        response = requests.post(API_URL, data={'query': query})

        # Check response status
        if response.status_code == 200:
            print("Data inserted successfully!")
            print("Response:", response.json())
        else:
            print("Failed to insert data!")
            print("Error:", response.json())
    except Exception as e:
        print("An error occurred:", str(e))


# Execute the script
if __name__ == "__main__":
    insert_sensor_data()
