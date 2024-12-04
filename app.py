from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
import json
import datetime
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)
socketio = SocketIO(app)


# Klass för att representera en radiokanal
class Channel():
    def __init__(self, name=None, id=None, siteurl=None, color=None, image=None, liveaudio=None, **kwargs):
        self.id = id
        self.name = name
        self.siteurl = siteurl
        self.color = color
        self.image = image
        self.liveaudio_url = liveaudio['url'] if liveaudio else 'No live audio available'

    def __repr__(self):
        return self.name


# Klass för att hantera anrop till Sveriges Radios API
class SverigesRadio():
    @classmethod
    def call(cls, method, payload={}):
        url = f'https://api.sr.se/api/v2/{method}'
        payload['format'] = 'json'
        response = requests.get(url, params=payload)
        if response.status_code != 200:
            return {}
        return json.loads(response.text)

    @classmethod
    def channels(cls):
        payload = dict(size=500)
        data = cls.call('channels', payload)
        channels = data.get('channels', [])
        return [Channel(**channel) for channel in channels]

    @classmethod
    def channel_schedule(cls, channel_id, all_programs=False):
        payload = {'channelid': channel_id, 'pagination': False}
        data = cls.call('scheduledepisodes', payload)
        schedule = data.get('schedule', [])

        # Filtrera för framtida program
        current_time = datetime.datetime.now()
        future_schedule = [prog for prog in schedule if convert_utc_to_local(prog['starttimeutc']) > current_time]

        # Begränsa till de första 10 programmen om inte alla program efterfrågas
        if not all_programs and len(future_schedule) > 10:
            return future_schedule[:10]
        return future_schedule


# Hjälpfunktion för att konvertera UTC-tid till lokal tid
def convert_utc_to_local(utc_time_str):
    try:
        timestamp = int(utc_time_str[6:-2]) // 1000
        return datetime.datetime.fromtimestamp(timestamp)
    except Exception as e:
        return None


# Flask-filter för att formatera datum och tid
@app.template_filter('format_datetime')
def format_datetime_filter(utc_time_str):
    local_time = convert_utc_to_local(utc_time_str)
    return local_time.strftime('%Y-%m-%d %H:%M:%S') if local_time else 'Ogiltig tid'


# MQTT-inställningar
MQTT_BROKER_URL = "localhost"  # MQTT-brokers adress
MQTT_BROKER_PORT = 1883  # MQTT-brokers port
MQTT_TOPIC = "sensor/data"  # önskat MQTT-ämne

# Global variabel för att lagra sensor data
sensor_data = {'Antal lysnare': 0}


def on_connect(client, userdata, flags, rc):
    print("Ansluten till MQTT-broker med resultatkod " + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    global sensor_data
    try:
        data = json.loads(msg.payload.decode())
        sensor_data['Antal lysnare'] = data.get('Antal lysnare', 0)
        print(f"Meddelande mottaget: {data}")  # Logga det mottagna meddelandet
        print(f"Uppdaterad sensor_data: {sensor_data}")  # Logga den uppdaterade sensor_data
        socketio.emit('sensor_update', {'antal_lyssnare': sensor_data['Antal lysnare']})
    except json.JSONDecodeError:
        print("Kunde inte avkoda MQTT-meddelandet")


def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, 60)
    client.loop_forever()


# Huvudvägen för att visa lista över kanaler
@app.route('/')
def index():
    channels = SverigesRadio.channels()
    return render_template('index.html', channels=channels)


# Väg för att visa programtablån för en specifik kanal
@app.route('/channel/<int:channel_id>')
def channel_detail(channel_id):
    channel = next((c for c in SverigesRadio.channels() if c.id == channel_id), None)
    if channel:
        schedule = SverigesRadio.channel_schedule(channel_id, all_programs=False)
        return render_template('channel_detail.html', channel=channel, schedule=schedule, all_programs=False,
                               listeners=sensor_data['Antal lysnare'])
    else:
        return "Kanal hittades inte", 404


# Väg för att visa alla program för en specifik kanal
@app.route('/channel/<int:channel_id>/all')
def channel_all_programs(channel_id):
    channel = next((c for c in SverigesRadio.channels() if c.id == channel_id), None)
    if channel:
        schedule = SverigesRadio.channel_schedule(channel_id, all_programs=True)
        return render_template('channel_detail.html', channel=channel, schedule=schedule, all_programs=True,
                               listeners=sensor_data['Antal lysnare'])
    else:
        return "Kanal hittades inte", 404


# Flask-väg för att visa sensor data
@app.route('/sensor')
def sensor():
    return render_template('sensor.html', data=sensor_data)


@socketio.on('connect')
def handle_connect(auth=None):
    emit('sensor_data', {'antal_lyssnare': sensor_data['Antal lysnare']})


# Kör Flask-applikationen med SocketIO
if __name__ == '__main__':
    # Starta MQTT-klienten i en separat tråd
    threading.Thread(target=start_mqtt_client, daemon=True).start()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
