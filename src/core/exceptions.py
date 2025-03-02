"""Exception classes for the multiagent system."""

class ApplicationError(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(ApplicationError):
    """Exception raised for validation errors."""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, status_code=400)

class NotFoundError(ApplicationError):
    """Exception raised when a resource is not found."""
    def __init__(self, resource_type: str, resource_id: str = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, status_code=404)

class AuthenticationError(ApplicationError):
    """Exception raised for authentication failures."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(ApplicationError):
    """Exception raised for authorization failures."""
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(message, status_code=403)

class ConfigurationError(ApplicationError):
    """Exception raised for configuration issues."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class ExternalServiceError(ApplicationError):
    """Exception raised for errors in external service calls."""
    def __init__(self, service: str, message: str):
        super().__init__(f"Error in {service}: {message}", status_code=502)

class RateLimitError(ApplicationError):
    """Exception raised when rate limits are exceeded."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)
