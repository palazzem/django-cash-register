from rest_framework.exceptions import APIException


class CashRegisterNotReady(APIException):
    """
    Generic exception when the communication with the cash
    register doesn't work properly
    """
    status_code = 500
    default_detail = 'The connected cash register is not ready. Please check the connection'
