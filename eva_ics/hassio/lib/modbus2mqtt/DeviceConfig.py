import logging
from TrackedSettings import TrackedSettings
from typing import List, Any, Dict
from MqttConfig import MqttConfig
from pydantic import Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import config



class DeviceConfig(TrackedSettings):
    """
    The base class for the device configuration. All devices must be derived from this class.
    """
    kind: str = Field(description="The device kind, used to load plugins")
    slave: int = Field(description="The Modbus slave address")
    manufacturer: str = Field(default="", description="The manufacturer of the device")
    model: str = Field(default="", description="The model of the device")
    allow_discovery: bool = Field(True, description="Allow MQTT discovery for the device. Useful for debugging, "
                                                    "so Eva will not publish and overwrite discovery")

    class Config:
        extra = "allow"

    def model_post_init(self, __context):
        """
        Constructor-like, called after the model initialized
        :param __context:
        """
        super().model_post_init(__context)
        self.initialize()
        if self.model == "":
            self.model = self.kind
        if self.manufacturer == "":
            self.manufacturer = "Unknown"

    def initialize(self):
        pass

    @property
    def eva_id(self) -> str:
        """
        The EVA ID of the device
        :return:
        """
        return f'{self.parent.id}-{self.id}'

    def build_discovery(self, item_type, payload=None, slug=None) -> Dict[str, Any]:
        """
        Build a discovery message for the entity exposed by the device
        :param item_type: the component type of the item (e.g. sensor, switch etc.
        `MQTT Discovery <https://www.home-assistant.io/integrations/mqtt/#configuration-via-mqtt-discovery>`_)

        :param payload:

        :param slug: The slug of the entity (e.g. switch1, humidity, temperature).
                If None, the entity will be published to the base topic

        :return: The discovery configuration : broker, payload and topic
        """
        rv = {
            "broker": self.mqtt.eva_id,
            "payload": {
                "device": {
                    "identifiers": [
                        f"{self.eva_id}"
                    ],
                    "connections": [
                        [
                            "eva_id",
                            f"{self.eva_id}"
                        ]
                    ],
                    "manufacturer": self.manufacturer,
                    "model": self.model,
                    "name": f"{self.eva_id}",
                    "via_device": "eva_modbus2mqtt"
                }
            }}
        if slug is not None:
            rv['payload']['object_id'] = f"{self.eva_id}_{slug}"
            rv['payload']['unique_id'] = f"{self.eva_id}_{slug}"
            rv["topic"] = f"{self.mqtt.get_discovery_topic()}/{item_type}/{self.eva_id}/{slug}/config"
            rv['payload']["state_topic"] = f"{self.mqtt.base_topic}/{self.eva_id}/{slug}"
            rv['payload']["json_attributes_topic"] = f"{self.mqtt.base_topic}/{self.eva_id}/{slug}"
        else:
            rv["topic"] = f"{self.mqtt.get_discovery_topic()}/{item_type}/{self.eva_id}/config"
            rv['payload']["state_topic"] = f"{self.mqtt.base_topic}/{self.eva_id}"
            rv['payload']["json_attributes_topic"] = f"{self.mqtt.base_topic}/{self.eva_id}"
        if payload is not None:
            rv['payload'] = {**rv['payload'], **payload}
        return rv

    @property
    def mqtt(self) -> MqttConfig:
        """
        returns the MQTT object for the device

        :return: MqttConfig
        """
        import config
        if self.parent.mqtt not in config.CONFIG.mqtt.keys():
            raise RuntimeError(f"No {self.parent.mqtt} broker")
        return config.CONFIG.mqtt[self.parent.mqtt]

    @property
    def puller_config(self) -> List[Dict[str, Any]]:
        """
        Builds puller configuration for EvaICS

        Refer to `Modbus master <https://info.bma.ai/en/actual/eva4/svc/eva-controller-modbus.html>`_

        Must be implemented in the derived class
        """
        raise Exception("Not implemented")

    @property
    def output_config(self) -> List[Dict[str, Any]]:
        """
        Builds basic output configuration for EvaICS
        Refer to `PubSub config <https://info.bma.ai/en/actual/eva4/svc/eva-controller-pubsub.html#output>`_

        :return: A list of dictionaries representing the output configuration
        """
        p = self.puller_config
        oids = []
        for i in p:
            for m in i['map']:
                oids.append(m['oid'])
        mapping = []
        for o in oids:
            r = o.split('/')[1]
            m = {"map": [
                {
                    "oid": o,
                    "path": f"$.value",
                    "prop": "value"
                },
                {
                    "oid": o,
                    "path": f"$.status",
                    "prop": "status"
                }
            ],
                "packer": "json",
                "topic": f"{self.mqtt.base_topic}/{self.eva_id}/{r}",
                "interval": 60
            }
            mapping.append(m)

        return mapping

    @property
    def action_map(self) -> Dict[str, Any]:
        """
        Builds action map for EvaICS

        :return: Dict[str, Any]
        """
        rv = {}
        x = self.input_config
        for k, v in x.items():
            rv[k] = {
                'type': v['type'],
                'unit': self.slave,
                'reg': v['reg'],
            }
        return rv

    @property
    def input_config(self) -> Dict[str, Any]:
        """
        Builds input configuration for EvaICS
        :return:
        """
        return {}

    @property
    def discovery(self) -> Dict[str, Any]:
        """
        Provides the discovery configuration for the device
        """
        raise Exception("Not implemented")
