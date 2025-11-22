from enum import Enum


class InteractionState(str, Enum):
    """Enum for the current state of interaction between characters."""
    
    NONE = "none"
    TALKING = "talking"
    KISSING = "kissing"
    FIGHTING = "fighting"
    ROMANCING = "romancing"
    USING_OBJECT = "using_object"

