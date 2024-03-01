from DeviceConfig import DeviceConfig
from typing import List, Any, Dict


class Device(DeviceConfig):

    def initialize(self):
        """
        Initializes the discovery - set manufacturer and model.
        """
        self.manufacturer = "Aliexpress"
        self.model = "XY-MD02"

    @property
    def puller_config(self) -> List[Dict[str, Any]]:
        """
        Builds puller configuration for EvaICS.

        :return: puller configuration
        """
        return [
            {
                "reg": "i1",
                "unit": self.slave,
                # here the two registers will be read at once because device supports it.
                "count": 2,
                "map": [
                    {
                        "offset": 0,
                        "oid": f"sensor:{self.eva_id}/temp",
                        "type": "int16",
                        "transform": [
                            {
                                "func": "divide",
                                "params": [10]
                            }
                        ]
                    },
                    {
                        # The second sensor is fetched from offset 1.
                        "offset": 1,
                        "oid": f"sensor:{self.eva_id}/hum",
                        "type": "int16",
                        "transform": [
                            {
                                # Device reports in integers, so 30% will be 300, we have to divide it.
                                # It is possible to divide in discovery through the value template
                                "func": "divide",
                                "params": [10]
                            }
                        ]

                    },
                ]

            }
        ]

    @property
    def discovery(self) -> List[Dict[str, Any]]:
        """

        Building the discovery message for sensors.

        :return: Discovery data
        """
        rv = [
            self.build_discovery(item_type="sensor",
                                 payload={"value_template": "{{ value_json.value | is_defined }}",
                                          "state_class": "measurement",
                                          "device_class": "Temperature",
                                          "unit_of_meas": "°C",
                                          },
                                 slug="temp"),
            self.build_discovery(item_type="sensor",
                                 payload={"value_template": "{{ value_json.value | is_defined }}",
                                          "state_class": "measurement",
                                          "device_class": "Humidity",
                                          "unit_of_meas": "%",
                                          },
                                 slug="hum")]
        return rv
