"""
Main PostgreSQL embedded class
"""

import os
import signal
import socket
import subprocess
import time
import atexit
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import psutil

from .config import PostgreSQLConfig
from .downloader import PostgreSQLDownloader
from .monitor import ProcessMonitor
from .exceptions import (
    PostgreSQLEmbeddedError, 
    PostgreSQLInstallError, 
    PostgreSQLStartError, 
    PostgreSQLStopError,
    PostgreSQLDatabaseError,
    PostgreSQLMonitorError
)


class PostgreSQL:
    """Embedded PostgreSQL database manager"""
    
    def __init__(self, config: Optional[PostgreSQLConfig] = None):
        self.config = config or PostgreSQLConfig()
        self.downloader = PostgreSQLDownloader(self.config)
        self.process: Optional[subprocess.Popen] = None
        self._is_initialized = False
        self._monitor: Optional[ProcessMonitor] = None
        self._logger = logging.getLogger(__name__)
        
        # Initialize process monitor if enabled
        if self.config.enable_monitoring:
            self._monitor = ProcessMonitor(self.config, self._restart_postgresql)
        
        # Register cleanup on exit
        if self.config.cleanup_on_exit:
            atexit.register(self.stop)
    
    def setup(self) -> None:
        """Download and install PostgreSQL if needed"""
        try:
            self.downloader.download_and_install()
            self._initialize_database()
        except Exception as e:
            raise PostgreSQLInstallError(f"Setup failed: {e}")
    
    def _initialize_database(self) -> None:
        """Initialize PostgreSQL database cluster"""
        if self._is_initialized:
            return
            
        data_dir = Path(self.config.data_dir)
        if data_dir.exists() and any(data_dir.iterdir()):
            self._is_initialized = True
            return
        
        # Create data directory
        os.makedirs(self.config.data_dir, exist_ok=True)
        
        # Initialize database cluster
        initdb_bin = self.downloader.get_initdb_bin_path()
        cmd = [
            str(initdb_bin),
            "-D", self.config.data_dir,
            "-U", self.config.username,
            "--locale=C",  # Use C locale to avoid locale issues
            "--encoding=UTF8",
            "--auth-local=trust",  # Use trust authentication for local connections
            "--auth-host=trust"    # Use trust for host connections too for embedded use
        ]
        
        try:
            # Set environment to avoid locale issues
            env = os.environ.copy()
            env["LC_ALL"] = "C"
            env["LANG"] = "C"
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise PostgreSQLInstallError(f"initdb failed: {stderr}")
                
            self._is_initialized = True
            
        except Exception as e:
            raise PostgreSQLInstallError(f"Database initialization failed: {e}")
    
    def start(self) -> None:
        """Start PostgreSQL server"""
        if self.is_running():
            return
            
        if not self._is_initialized:
            raise PostgreSQLStartError("Database not initialized. Call setup() first.")
        
        # Find available port if not specified
        if self.config.port is None:
            self.config.port = self._find_free_port()
        
        # Create postgresql.conf
        self._create_config_file()
        
        # Start PostgreSQL
        postgres_bin = self.downloader.get_postgres_bin_path()
        cmd = [
            str(postgres_bin),
            "-D", self.config.data_dir,
            "-p", str(self.config.port),
            "-h", self.config.host
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            self._wait_for_server_start()
            
            # Start monitoring if enabled
            if self._monitor:
                self._monitor.start_monitoring(self.is_running)
                self._logger.info("Started PostgreSQL process monitoring")
            
        except Exception as e:
            raise PostgreSQLStartError(f"Failed to start PostgreSQL: {e}")
    
    def stop(self) -> None:
        """Stop PostgreSQL server"""
        if not self.is_running():
            return
            
        try:
            # Stop monitoring first
            if self._monitor:
                self._monitor.stop_monitoring()
                self._logger.info("Stopped PostgreSQL process monitoring")
            
            if self.process:
                # Send SIGTERM to gracefully shutdown
                self.process.terminate()
                
                # Wait for process to terminate
                try:
                    self.process.wait(timeout=self.config.timeout)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
                
        except Exception as e:
            raise PostgreSQLStopError(f"Failed to stop PostgreSQL: {e}")
    
    def is_running(self) -> bool:
        """Check if PostgreSQL server is running"""
        if self.process is None:
            return False
            
        return self.process.poll() is None
    
    def create_database(self, database_name: str) -> None:
        """Create a new database"""
        if not self.is_running():
            raise PostgreSQLDatabaseError("PostgreSQL server is not running")
        
        createdb_bin = self.downloader.get_createdb_bin_path()
        cmd = [
            str(createdb_bin),
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.username,
            database_name
        ]
        
        try:
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.password
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            if result.returncode != 0:
                raise PostgreSQLDatabaseError(f"Failed to create database '{database_name}': {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise PostgreSQLDatabaseError(f"Timeout creating database '{database_name}'")
        except Exception as e:
            raise PostgreSQLDatabaseError(f"Error creating database '{database_name}': {e}")
    
    def drop_database(self, database_name: str) -> None:
        """Drop a database"""
        if not self.is_running():
            raise PostgreSQLDatabaseError("PostgreSQL server is not running")
        
        dropdb_bin = self.downloader.get_dropdb_bin_path()
        cmd = [
            str(dropdb_bin),
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.username,
            database_name
        ]
        
        try:
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.password
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            if result.returncode != 0:
                raise PostgreSQLDatabaseError(f"Failed to drop database '{database_name}': {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise PostgreSQLDatabaseError(f"Timeout dropping database '{database_name}'")
        except Exception as e:
            raise PostgreSQLDatabaseError(f"Error dropping database '{database_name}': {e}")
    
    def database_exists(self, database_name: str) -> bool:
        """Check if a database exists"""
        if not self.is_running():
            raise PostgreSQLDatabaseError("PostgreSQL server is not running")
        
        psql_bin = self.downloader.get_psql_bin_path()
        cmd = [
            str(psql_bin),
            "-h", self.config.host,
            "-p", str(self.config.port),
            "-U", self.config.username,
            "-d", "postgres",
            "-t", "-c",
            f"SELECT 1 FROM pg_database WHERE datname='{database_name}'"
        ]
        
        try:
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.password
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            return result.returncode == 0 and "1" in result.stdout.strip()
            
        except Exception:
            return False
    
    def get_connection_url(self, database_name: str = "postgres") -> str:
        """Get PostgreSQL connection URL"""
        return (
            f"postgresql://{self.config.username}:{self.config.password}@"
            f"{self.config.host}:{self.config.port}/{database_name}"
        )
    
    def _find_free_port(self) -> int:
        """Find a free port for PostgreSQL"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def _create_config_file(self) -> None:
        """Create postgresql.conf file"""
        config_path = Path(self.config.data_dir) / "postgresql.conf"
        
        config_lines = [
            f"port = {self.config.port}",
            f"listen_addresses = '{self.config.host}'",
            "logging_collector = off",
            "log_destination = 'stderr'",
        ]
        
        # Add custom configuration
        for key, value in self.config.postgres_config.items():
            config_lines.append(f"{key} = '{value}'")
        
        with open(config_path, 'w') as f:
            f.write('\n'.join(config_lines) + '\n')
    
    def _wait_for_server_start(self) -> None:
        """Wait for PostgreSQL server to start accepting connections"""
        start_time = time.time()
        
        while time.time() - start_time < self.config.timeout:
            if not self.is_running():
                raise PostgreSQLStartError("PostgreSQL process died during startup")
            
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((self.config.host, self.config.port))
                    if result == 0:
                        return
            except Exception:
                pass
            
            time.sleep(0.1)
        
        raise PostgreSQLStartError(f"PostgreSQL failed to start within {self.config.timeout} seconds")
    
    def _restart_postgresql(self) -> None:
        """Internal method to restart PostgreSQL (used by monitor)"""
        self._logger.info("Restarting PostgreSQL due to process death")
        
        # Clean up the dead process
        if self.process:
            self.process = None
        
        # Restart PostgreSQL
        self.start()
    
    def enable_monitoring(self) -> None:
        """Enable process monitoring for running PostgreSQL instance"""
        if not self._monitor:
            self._monitor = ProcessMonitor(self.config, self._restart_postgresql)
        
        if self.is_running():
            self._monitor.start_monitoring(self.is_running)
            self._logger.info("Enabled PostgreSQL process monitoring")
        else:
            raise PostgreSQLMonitorError("Cannot enable monitoring: PostgreSQL is not running")
    
    def disable_monitoring(self) -> None:
        """Disable process monitoring"""
        if self._monitor:
            self._monitor.stop_monitoring()
            self._logger.info("Disabled PostgreSQL process monitoring")
    
    def get_monitoring_status(self) -> dict:
        """Get current monitoring status"""
        if not self._monitor:
            return {
                "is_monitoring": False,
                "monitoring_enabled": False,
                "restart_count": 0,
                "last_restart_time": None,
                "max_restart_attempts": self.config.max_restart_attempts,
                "auto_restart_enabled": self.config.auto_restart
            }
        
        return self._monitor.get_status()
    
    def reset_restart_count(self) -> None:
        """Reset the restart attempt counter"""
        if self._monitor:
            self._monitor.reset_restart_count()
            self._logger.info("Reset restart attempt counter")
    
    def __enter__(self):
        """Context manager entry"""
        self.setup()
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
