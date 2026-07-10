class AppException(Exception):
    def __init__(self, detail: str | None = None):
        self.detail = detail
