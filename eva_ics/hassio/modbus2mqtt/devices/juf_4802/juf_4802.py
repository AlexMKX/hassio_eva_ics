import DeviceConfig
from typing import List, Any, Dict
import jinja2
import yaml


class Device(DeviceConfig.DeviceConfig):
    default_speed: int = 25

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
        rv = {
            f"unit:{self.eva_id}/duty_perc": {
                "topic": f"{self.mqtt.base_topic}/{self.eva_id}/duty_perc/set",
                "type": "uint16",
                "reg": "h3"
            }
        }
        return rv

    @property
    def discovery(self) -> List[Dict[str, Any]]:
        rv = []
        fan = self.build_discovery(item_type="fan",
                                   payload={"device_class": "fan",
                                            "command_topic": f"{self.mqtt.base_topic}/{self.eva_id}/duty_perc",
                                            "state_value_template":
                                                "{{ 'ON' if value_json.value>0 else 'OFF' }}",
                                            "command_template":
                                                f"{{{{ 0 if value=='OFF' else "
                                                f"{self.default_speed} if value=='ON' else value }}}}",
                                            "percentage_command_topic":
                                                f"{self.mqtt.base_topic}/{self.eva_id}/duty_perc/set",
                                            "percentage_state_topic": f"{self.mqtt.base_topic}/{self.eva_id}/duty_perc",
                                            "percentage_value_template":
                                                "{{ value_json.value | is_defined }}",
                                            "state_topic": f"{self.mqtt.base_topic}/{self.eva_id}/duty_perc",
                                            "availability_topic": f"{self.mqtt.base_topic}/{self.eva_id}/duty_perc",
                                            "name": f"{self.eva_id} Fan",
                                            },
                                   slug="fan")
        rv.append(fan)
        for x in range(1, 5):
            rv.append(self.build_discovery(item_type="sensor",
                                           payload={
                                               "value_template": f"{{{{ value_json.value | is_defined }}}}",
                                               "state_class": "measurement",
                                               "unit_of_meas": "RPM",
                                               "name": f"Fan{x} RPM",
                                           },
                                           slug=f"fan{x}_rpm"))

        return rv
