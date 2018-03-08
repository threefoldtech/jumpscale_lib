"""
Define Exceptions
"""

class RESTAPIError(Exception):
    """
    RESTAPI Error
    """


class BACKENDError(Exception):
    """
    Error representing a problem with the content of backend response
    """
    