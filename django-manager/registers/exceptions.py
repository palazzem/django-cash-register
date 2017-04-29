from rest_framework.exceptions import APIException


class AdapterPushFailed(APIException):
    """
    Generic exception that happens when the communication with
    an external service failed. When using Adapters, you should
    expect a failure with this parent exception.
    """
    status_code = 500
    default_detail = 'Adapter was unable to push data to the service.'


class CashRegisterNotReady(AdapterPushFailed):
    """
    Exception when the communication with the cash register
    doesn't work properly.
    """
    default_detail = 'The connected cash register is not ready. Please check the connection'
