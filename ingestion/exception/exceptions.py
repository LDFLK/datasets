from fastapi import HTTPException, status

class NotFoundError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)

class BadRequestError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

class InternalServerError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)

class ServiceUnavailableError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=message)

class GatewayTimeoutError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=message)
