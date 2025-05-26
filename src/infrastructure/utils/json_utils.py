"""
Utility functions and classes for JSON operations

Provides general-purpose functionality for JSON data conversion and processing.
"""

import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    """
    JSON encoder that converts datetime objects to ISO format strings

    Extends the standard JSON encoder to enable serialization of datetime objects.
    """

    def default(self, obj):
        """
        Define the serialization method for objects

        Args:
            obj: Object to be serialized

        Returns:
            Serialized value
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)
