# Helios KWL-EC300 RS485 to MQTT (with Dsicoverable Feature for HomeAssistant)
#
# uses the HA_MQTT_discoverable library https://github.com/unixorn/ha-mqtt-discoverable/ 
# and the helios library https://github.com/mtiews/smarthomepy-helios
#

from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import Number, NumberInfo, BinarySensor, BinarySensorInfo, Sensor, SensorInfo, DeviceInfo, Switch, SwitchInfo
from paho.mqtt.client import Client, MQTTMessage
from helios import HeliosBase, Helios
import time

# change as required:
serialport = '/dev/ttyUSB'

# Configure the required parameters for the MQTT broker, you may need to add user/pass
mqtt_settings = Settings.MQTT(host="localhost")

# To receive number updates from HA, define a callback function:
def fan_callback(client: Client, user_data, message: MQTTMessage):
    number = int(message.payload.decode())
    
    print(f"Fanspeed set to {number}")

    helios.writeValue('fanspeed',number)

    # Send an MQTT message to confirm to HA that the fanspeed was changed
    my_fan.set_value(number)

# To receive Power updates from HA, define a callback function:
def power_callback(client: Client, user_data, message: MQTTMessage):
    power = message.payload.decode()

    print(f"Received Power state: {power}")

    # Send an MQTT message to confirm the powerstate to HA
    if power == "ON":
        # power on Helios:
        helios.writeValue('power_state',1)
        # update HA switch:
        powerswitch.on()

    elif power == "OFF":
        # power off Helios:
        helios.writeValue('power_state',0)
        # update HA switch:
        powerswitch.off()


# Define the device. At least one of `identifiers` or `connections` must be supplied
device_info = DeviceInfo(name="Helios KWL-EC300", identifiers="helios_ec300", manufacturer="Helios", model="KWL-EC300")

# Information about the `fan` entity.
fan_info = NumberInfo(name="Fan", min=2, max=8, mode="slider", step=1, unique_id="helios_fan", device=device_info)
fansettings = Settings(mqtt=mqtt_settings, entity=fan_info)
# Instantiate the number
my_fan = Number(fansettings, fan_callback)

# Binary Switch Sensor
switch_info = SwitchInfo(name="Power", unique_id="helios_power_switch", device=device_info)
binsettings = Settings(mqtt=mqtt_settings, entity=switch_info)
# Instantiate the sensor
powerswitch = Switch(binsettings, power_callback)

# Binary Sensor
bypass_info = BinarySensorInfo(name="ByPass", unique_id="helios_bypass", device=device_info)
bypasssettings = Settings(mqtt=mqtt_settings, entity=bypass_info)
# Instantiate the sensor
bypasssensor = BinarySensor(bypasssettings)


sensors = {}
def sendUpdate(name, unique_id, devclass, uofm, mqtt_settings, device_info, value):
    sensor = sensors.get(name)
    if (sensor is None):
        sensor_info = SensorInfo(unit_of_measurement=uofm, 
                                name=name, 
                                device_class=devclass,
                                unique_id=unique_id, 
                                device=device_info)
        sensor = Sensor(Settings(mqtt=mqtt_settings, entity=sensor_info))
        sensors[name] = sensor
        time.sleep(0.1)
    sensor.set_state(value)


try:
    helios = HeliosBase(serialport)
    helios.connect()
    if not helios._is_connected:
        raise Exception("Not connected")
    
    while True:

        # Get Temperatures
        sendUpdate( 'Outside Temp', "kwl_outside_temp",  "temperature", "°C", mqtt_settings, device_info,helios.readValue('outside_temp'));
        sendUpdate( 'Exhaust Temp',   "kwl_exhaust_temp",  "temperature", "°C", mqtt_settings, device_info,helios.readValue('exhaust_temp'));
        sendUpdate( 'Inside Temp',     "kwl_inside_temp",   "temperature", "°C", mqtt_settings, device_info,helios.readValue('inside_temp'));
        sendUpdate( 'Incoming Temp',     "kwl_incoming_temp", "temperature", "°C", mqtt_settings, device_info,helios.readValue('incoming_temp'));
        sendUpdate( 'Bypass Temp',     "kwl_bypass_temp", "temperature", "°C", mqtt_settings, device_info,helios.readValue('bypass_temp'));

        # Get FAN Speed
        fanspeed = int(helios.readValue('fanspeed'))
        my_fan.set_value(fanspeed) # update HomeAssistant

        # Get Power State
        if helios.readValue('power_state') == 1:
            powerswitch.on()
        else:
            powerswitch.off()

        # Get Bypass Status
        bypass = int(helios.readValue('bypass_disabled'))
        if bypass:
            bypasssensor.off()
        else:
            bypasssensor.on()

        time.sleep(10)

except Exception as e:
    print("Exception: {0}".format(e))
    exit
finally:
    if helios:
        helios.disconnect()