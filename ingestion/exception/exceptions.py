class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

class NotFoundError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=404, detail=message)

class BadRequestError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)

class InternalServerError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=500, detail=message)

class ServiceUnavailableError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=503, detail=message)

class GatewayTimeoutError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=504, detail=message)
