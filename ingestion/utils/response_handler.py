from ingestion.exception.exceptions import (
    BadRequestError, 
    NotFoundError, 
    InternalServerError, 
    ServiceUnavailableError, 
    GatewayTimeoutError
)

async def handle_api_response(response, error_prefix="API Error"):
    """
    Handle HTTP response and raise appropriate custom exceptions based on status code.
    
    Args:
        response: The aiohttp response object
        error_prefix (str): Prefix for the error message
        
    Returns:
        dict: The JSON response if status is 200 or 201
        
    Raises:
        HTTPException: Corresponding custom exception for the HTTP status code
        Exception: Generic exception for unmapped error status codes
    """
    if response.status == 200 or response.status == 201:
        return await response.json()
    
    error_text = await response.text()
    message = f"{error_prefix}: {response.status} - {error_text}"
    
    exception_map = {
        400: BadRequestError,
        404: NotFoundError,
        500: InternalServerError,
        503: ServiceUnavailableError,
        504: GatewayTimeoutError
    }
    
    exception_cls = exception_map.get(response.status)
    if exception_cls:
        raise exception_cls(message)
    else:
        raise Exception(message)
