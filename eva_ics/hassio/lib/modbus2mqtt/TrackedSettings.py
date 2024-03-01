from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import PrivateAttr


class TrackedSettings(BaseSettings):
    """
    The class that allows to track the parent of the current item and item's ID within the Pydantic structure

    """
    _id: str = PrivateAttr()
    _parent: TrackedSettings = PrivateAttr()

    def model_post_init(self, __context):
        self.propagate_children()

    def propagate_children(self):
        for f in self.model_fields:
            x = getattr(self, f)
            if issubclass(x.__class__, dict):
                for k, v in x.items():
                    if issubclass(v.__class__, TrackedSettings):
                        v._id = k
                        v._parent = self
            elif issubclass(x.__class__, TrackedSettings):
                x._id = None
                x._parent = self

    @property
    def id(self):
        """
            returns current ID in case this item is inside the dictionary
        :return:
        """
        return f'{self._id}'

    @property
    def parent(self):
        """
            returns the parent of this item within Pydantic structure
        :return:
        """
        return self._parent
