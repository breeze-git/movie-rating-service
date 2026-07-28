class AppError(Exception):
    title: str = "Bad Request"
    detail: str = "The request cannot be processed due to incorrect data."
    code: str = "BAD_REQUEST"

    def __init__(self, **kwargs):
        super().__init__(self.detail)

        self.extra = kwargs
