"""
Embed PostgreSQL - A Python library for embedding PostgreSQL databases

This library provides an embedded-like experience for PostgreSQL similar to what 
you would have with SQLite. It downloads and installs PostgreSQL during runtime
and manages the database lifecycle.
"""

from .postgresql import PostgreSQL
from .config import PostgreSQLConfig
from .monitor import ProcessMonitor
from .exceptions import (
    PostgreSQLEmbeddedError, 
    PostgreSQLInstallError, 
    PostgreSQLStartError,
    PostgreSQLStopError,
    PostgreSQLDatabaseError,
    PostgreSQLMonitorError
)

__version__ = "0.1.0"
__all__ = [
    "PostgreSQL", 
    "PostgreSQLConfig", 
    "ProcessMonitor",
    "PostgreSQLEmbeddedError", 
    "PostgreSQLInstallError", 
    "PostgreSQLStartError",
    "PostgreSQLStopError",
    "PostgreSQLDatabaseError",
    "PostgreSQLMonitorError"
]
