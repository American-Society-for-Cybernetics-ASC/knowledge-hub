class PaymentError(Exception):
    """Raised when an error occurs within the Payment Module."""

class NoProviderConfiguredError(PaymentError):
    """Raised when a call is attempted from the Payment Module with no configured provider."""

class PaymentProviderError(PaymentError):
    """Raised when a payment provider fails to fulfil a transaction request."""