class AppException(Exception):
    def __init__(self, detail: str | None = None):
        super().__init__(detail)
        self.detail = detail
