class AppException(Exception):
    title: str = "Bad Request"
    public_msg: str = "The request cannot be processed due to incorrect data."
    base_code: str = "BAD_REQUEST"

    def __init__(self, internal_msg, public_msg: str | None = None, code: str | None = None):
        self.internal_msg = internal_msg

        if public_msg is not None:
            self.public_msg = public_msg

        self.code = code or self.base_code

        super().__init__(internal_msg)
