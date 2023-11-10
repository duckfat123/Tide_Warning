import requests
import datetime

# NOAA API endpoint for tide predictions
TIDE_PREDICTIONS_URL = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'

# Station ID for Kahului Harbor
STATION_ID = '1615680'  # The station ID for Kahului Harbor

# Set up parameters for the API call
params = {
    'begin_date': datetime.datetime.now().strftime('%Y%m%d'),  # Today's date
    'end_date': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y%m%d'),  # Next day's date for a 24-hour range
    'station': STATION_ID,
    'product': 'predictions',
    'datum': 'MLLW',  # Mean Lower Low Water datum
    'units': 'english',  # Unit in feet
    'time_zone': 'lst_ldt',  # Local Standard/Daylight Time
    'format': 'json',  # Response format
    'interval': '6',  # Using 6-minute intervals as finer intervals are not supported
    'application': 'web_services',  # Application type
}

# Make the API request
response = requests.get(TIDE_PREDICTIONS_URL, params=params)

# Initialize variables to track the low tide windows
low_tide_start = None
low_tide_windows = []

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    tide_data = response.json()

    # Extract predictions
    predictions = tide_data.get('predictions', [])

    # Loop through the predictions to find low tide windows
    for pred in predictions:
        tide_height = float(pred['v'])
        tide_time = pred['t']
        if tide_height < 0.04:
            # If tide is below the threshold and we haven't started a window, start one
            if low_tide_start is None:
                low_tide_start = tide_time
        else:
            # If tide goes above the threshold and we are in a window, end it
            if low_tide_start is not None:
                low_tide_windows.append((low_tide_start, tide_time))
                low_tide_start = None

    # If we're still in a window at the end of the data, close it with the last timestamp
    if low_tide_start is not None:
        low_tide_windows.append((low_tide_start, predictions[-1]['t']))

    # Output the low tide windows
    for window in low_tide_windows:
        print(f"Low tide window: from {window[0]} to {window[1]}")
else:
    print("Failed to retrieve data: Status code {}".format(response.status_code))
