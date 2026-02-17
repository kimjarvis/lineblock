from pydantic import BaseModel, Field, model_validator
from typing import Union, Optional
from enum import Enum


class ConfigType(str, Enum):
    SOURCE = "source"
    SINK = "sink"
    END = "end"


class Source(BaseModel):
    source: str
    shift: Optional[int] = Field(None)

    model_config = {
        "extra": "forbid"  # This ensures no extra keys are allowed
    }


class Sink(BaseModel):
    sink: str

    model_config = {
        "extra": "forbid"  # This ensures no extra keys are allowed
    }


class End(BaseModel):
    end: bool

    model_config = {
        "extra": "forbid"  # This ensures no extra keys are allowed
    }

    @model_validator(mode='after')
    def validate_only_end(self):
        """Additional validation to ensure 'end' is properly structured"""
        # This is more of a safeguard since extra keys are already forbidden
        # But we can add logic here if needed
        return self


def validate_config(data: dict) -> Union[Source, Sink, End]:
    """
    Validate a dictionary by loading it into the appropriate Pydantic model.

    Args:
        data: Dictionary to validate

    Returns:
        An instance of Source, Sink, or End

    Raises:
        ValueError: If the dictionary doesn't contain one of the required keys
                   or fails validation
    """
    if not data:
        raise ValueError("Dictionary must contain at least one key")

    # Check which configuration type we have
    keys = set(data.keys())

    if "end" in keys:
        if len(keys) > 1:
            raise ValueError("When 'end' is present, it must be the only key in the dictionary")
        return End(**data)

    elif "source" in keys:
        # Let Pydantic handle validation of types and extra keys
        return Source(**data)

    elif "sink" in keys:
        return Sink(**data)

    else:
        raise ValueError("Dictionary must contain one of: 'source', 'sink', or 'end' key")


# Example usage and testing
if __name__ == "__main__":
    # Valid cases
    print("Valid cases:")
    try:
        result = validate_config({"end": True})
        print(f"✓ end: {result}")
    except Exception as e:
        print(f"✗ end: {e}")

