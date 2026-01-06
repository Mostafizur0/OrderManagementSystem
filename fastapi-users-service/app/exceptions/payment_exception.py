from app.middleware.metrics_middleware import TOTAL_PAYMENT_ERRORS


class PaymentException(Exception):
    """Base class for payment-related exceptions."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        TOTAL_PAYMENT_ERRORS.labels(error_type=self.__class__.__name__).inc(1)
