"""
Custom exceptions for embed-postgres library
"""


class PostgreSQLEmbeddedError(Exception):
    """Base exception for all embed-postgres related errors"""
    pass


class PostgreSQLInstallError(PostgreSQLEmbeddedError):
    """Raised when PostgreSQL installation fails"""
    pass


class PostgreSQLStartError(PostgreSQLEmbeddedError):
    """Raised when PostgreSQL fails to start"""
    pass


class PostgreSQLStopError(PostgreSQLEmbeddedError):
    """Raised when PostgreSQL fails to stop"""
    pass


class PostgreSQLDatabaseError(PostgreSQLEmbeddedError):
    """Raised when database operations fail"""
    pass


class PostgreSQLMonitorError(PostgreSQLEmbeddedError):
    """Raised when process monitoring encounters errors"""
    pass
