from DeviceConfig import DeviceConfig
from typing import List, Any, Dict


class Device(DeviceConfig):

    def initialize(self):
        """
        Initializes the discovery - set manufacturer and model.
        """
        self.manufacturer = "ZGCJ"
        self.model = "CJ-YBT"

    @property
    def puller_config(self) -> List[Dict[str, Any]]:
        """
        Builds puller configuration for EvaICS.

        :return: puller configuration
        """
        return [
            {
                "reg": "h4",
                "unit": self.slave,
                "count": 1,
                "map": [
                    {
                        "offset": 0,
                        "oid": f"sensor:{self.eva_id}/level",
                        "type": "int16",
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
                                          "device_class": "distance",
                                          "unit_of_meas": "cm",
                                          },
                                 slug="level")]
        return rv
