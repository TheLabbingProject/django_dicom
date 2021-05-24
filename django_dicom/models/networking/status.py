"""
Definition of the :class:`ServerStatus` Enum.
"""
from enum import Enum


class ServerStatus(Enum):
    """
    Represents the different states an association with some storage SCP may
    have.
    """

    DOWN = "Down"
    INACTIVE = "Inactive"
    UP = "Up"
