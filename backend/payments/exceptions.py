class PaymentError(Exception):
    """Raised when an error occurs within the Payment Module."""


class NoProviderConfiguredError(PaymentError):
    """Raised when a call is attempted from the Payment Module with no configured provider."""


class PaymentProviderError(PaymentError):
    """Raised when a payment provider fails to fulfil a transaction request."""


class PaymentNotFoundError(PaymentError):
    """Raised when a payment with the specified details does not exist."""


class PaymentAlreadyComplete(PaymentError):
    """Raised when a payment has already been paid."""


class TransactionNotSuccessful(PaymentError):
    """Raised when a transaction was not successful."""
