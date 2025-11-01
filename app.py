from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

# ✅ Your OpenWeatherMap API Key
API_KEY = "24cdd3a20c6b937b0990aed905d6f7c6"
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"


@app.route('/', methods=['GET', 'POST'])
def index():
    # ✅ Initialize variables
    city_name = ""
    weather_data = []
    error_msg = ""

    # ✅ Check if data is submitted through the form
    if request.method == 'POST':
        city_name = request.form.get('city').strip()

        # ✅ City input validation
        if city_name:
            try:
                # ✅ API Request to fetch 5-day Forecast Data
                params = {
                    'q': city_name,
                    'appid': API_KEY,
                    'units': 'metric'
                }
                response = requests.get(BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                # ✅ If API returns error (wrong city name)
                if data.get("cod") != "200":
                    error_msg = f"City '{city_name}' not found."
                else:
                    # ✅ Organizing forecast data day-wise
                    daily_summary = {}
                    for entry in data['list']:
                        date = datetime.fromtimestamp(entry['dt']).strftime('%Y-%m-%d')
                        temp = entry['main']['temp']
                        humidity = entry['main']['humidity']
                        wind_speed = entry['wind']['speed']
                        desc = entry['weather'][0]['description']
                        icon = entry['weather'][0]['icon']

                        # ✅ If date not added, initialize dictionary
                        if date not in daily_summary:
                            daily_summary[date] = {
                                'temps': [],
                                'humidities': [],
                                'winds': [],
                                'descs': [],
                                'icon': icon  # ✅ Latest weather icon
                            }

                        # ✅ Add weather conditions in list for averaging
                        daily_summary[date]['temps'].append(temp)
                        daily_summary[date]['humidities'].append(humidity)
                        daily_summary[date]['winds'].append(wind_speed)
                        daily_summary[date]['descs'].append(desc)

                    # ✅ Average values for each day
                    for date, info in daily_summary.items():
                        avg_temp = round(sum(info['temps']) / len(info['temps']), 1)
                        avg_humidity = round(sum(info['humidities']) / len(info['humidities']), 1)
                        avg_wind = round(sum(info['winds']) / len(info['winds']), 1)
                        desc = max(set(info['descs']), key=info['descs'].count)
                        weather_data.append({
                            'date': date,
                            'temp': avg_temp,
                            'humidity': avg_humidity,
                            'wind': avg_wind,
                            'desc': desc.title(),
                            'icon': info['icon']
                        })

            except Exception as e:
                # ✅ If API fetch fails
                error_msg = f"Error fetching data: {str(e)}"

        else:
            # ✅ Empty input field
            error_msg = "Please enter a city name."

    # ✅ Sending processed data back to HTML template
    return render_template('index.html', weather_data=weather_data, city=city_name, error=error_msg)


if __name__ == "__main__":
    # ✅ Debug mode helps during development
    app.run(debug=True)
