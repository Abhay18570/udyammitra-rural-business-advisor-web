class ProviderError(Exception):
    """Public-safe provider failure; never contains request URLs or profile data."""
    def __init__(self, code="PROVIDER_UNAVAILABLE", status=503, retry_after=None):
        super().__init__(code)
        self.code = code
        self.status = status
        self.retry_after = retry_after
