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

class InsufficientWalletFundsError(Exception):
    """
    Error representing an insufficient wallet funds while creating a transaction
    """

class NonExistingOutputError(Exception):
    """
    Error representing a non-existing output referenced in a transaction
    """