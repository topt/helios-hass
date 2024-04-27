# helios-hass
Helios KWL-EC300 ventilation RS485 to MQTT with HomeAssistant discoverable 

## Hardware
just connect your Helios using a RS-485 adapter.

I connected it in parallel to the remote, see this project for sample wiring:
https://github.com/lostcontrol/esphome-helios-kwl

USB-RS-485 adapter, e.g. something like this https://www.aliexpress.com/item/1005006827649035.html should work.

## Software
This requires a few libraries:
  * the HA_MQTT_discoverable library https://github.com/unixorn/ha-mqtt-discoverable/ 
  * the helios library https://github.com/mtiews/smarthomepy-helios
  * pyserial

pyserial and the ha-mqtt-discoverable can be installed using pip:

```
python3 -m venv venv
cd venv
source bin/activate
pip install ha-mqtt-discoverable pyserial
```
put the helios library in a directory called helios

adapt the config variables in the script, mainly the USB device, and the MQTT broker settings:
```
# change as required:
serialport = '/dev/ttyUSB'

# Configure the required parameters for the MQTT broker, you may need to add user/pass
mqtt_settings = Settings.MQTT(host="localhost")
```

now, with the venv activated, you can run
```
python3 helios-ha.py 
```

use your favorite method to make it run as a daemon.
