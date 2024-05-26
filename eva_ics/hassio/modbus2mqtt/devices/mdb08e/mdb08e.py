import DeviceConfig
from typing import List, Any, Dict
import jinja2
import yaml


class Device(DeviceConfig.DeviceConfig):

    @property
    def puller_config(self) -> List[Dict[str, Any]]:
        """
        Builds puller configuration for EvaICS.
        Loads puller configuration from jinja2 template and renders it with the current object.
        :return:
        """
        import os
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                 undefined=jinja2.StrictUndefined)
        t = env.get_template("puller.yml.j2").render(item=self)
        return yaml.safe_load(t)

    @property
    def input_config(self) -> Dict[str, Any]:
        """
        Builds input configuration for EvaICS to pass data from MQTT to Modbus.
        Please refer to `MQTT input
        <https://info.bma.ai/en/actual/eva4/svc/eva-controller-pubsub.html?highlight=mqtt#input>`_
        :return:
        """
        rv = {}
        for i in range(8):
            rv[f"unit:{self.eva_id}/relay{i}"] = {
                "topic": f"{self.mqtt.base_topic}/{self.eva_id}/relay_{i}/set",
                "reg": f"c{i}"
            }
        return rv

    @property
    def discovery(self) -> List[Dict[str, Any]]:
        rv = []
        x = {
            "availability": [
                {
                    "topic": "zigbee2mqtt/bridge/state",
                    "value_template": "{{ value_json.state }}"
                },
                {
                    "topic": "zigbee2mqtt/out-porch-light-all-2/availability",
                    "value_template": "{{ value_json.state }}"
                }
            ],
            "availability_mode": "all",
            "command_topic": "zigbee2mqtt/out-porch-light-all-2/l1/set",
            "device": {
                "identifiers": [
                    "zigbee2mqtt_0xa4c138585fe50e0a"
                ],
                "manufacturer": "TuYa",
                "model": "2 gang switch module (TS0002_switch_module)",
                "name": "out-porch-light-all-2",
                "via_device": "zigbee2mqtt_bridge_0x00124b0014da3d4d"
            },
            "json_attributes_topic": "zigbee2mqtt/out-porch-light-all-2",
            "name": "L1",
            "object_id": "out-porch-light-all-2_l1",
            "origin": {
                "name": "Zigbee2MQTT",
                "sw_version": "1.37.1",
                "support_url": "https://www.zigbee2mqtt.io"
            },
            "payload_off": "OFF",
            "payload_on": "ON",
            "state_topic": "zigbee2mqtt/out-porch-light-all-2",
            "unique_id": "0xa4c138585fe50e0a_switch_l1_zigbee2mqtt",
            "value_template": "{{ value_json.state_l1 }}",
            "platform": "mqtt"
        }
        for i in range(0):
            disc = self.build_discovery(item_type="switch",
                                        payload={"device_class": "switch",
                                                 "command_topic": f"{self.mqtt.base_topic}/{self.eva_id}/relay_{i}/set",
                                                 "state_value_template":
                                                     "{{ 'ON' if value_json.value>0 else 'OFF' }}",
                                                 "command_template":
                                                     f"{{{{ 0 if value=='OFF' else "
                                                     f"128 if value=='ON' else value }}}}",
#                                                 "state_topic": f"{self.mqtt.base_topic}/{self.eva_id}/duty_perc",
#                                                 "availability_topic": f"{self.mqtt.base_topic}/{self.eva_id}/duty_perc",
                                                 "name": f"{self.eva_id} Fan",
                                                 },
                                        slug=f"relay_{i}")
            rv.append(disc)
        return rv
