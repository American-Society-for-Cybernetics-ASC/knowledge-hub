class PaymentError(Exception):
    """Raised when an error occurs within the Payment Module."""


class PaymentProviderNotFoundError(PaymentError):
    """Raised when a call is attempted from the Payment Module for a nonexistant payment provider."""


class PaymentNotYoursError(PaymentError):
    """Raised when a call is attempted from the Payment Module for a payment that the caller doesn't own."""


class PaymentProviderError(PaymentError):
    """Raised when a payment provider fails to fulfil a transaction request."""


class PaymentNotFoundError(PaymentError):
    """Raised when a payment with the specified details does not exist."""


class TransactionNotFoundError(PaymentError):
    """Raised when a payment with the specified details does not exist."""


class PaymentAlreadyComplete(PaymentError):
    """Raised when a payment has already been paid."""


class TransactionNotSuccessful(PaymentError):
    """Raised when a transaction was not successful."""


class TransactionInProgressError(PaymentError):
    """Raised when a transaction is already in progress"""

class CurrencyConversionError(PaymentError):
    """Raised when the the currency conversion failed to be calculated."""
