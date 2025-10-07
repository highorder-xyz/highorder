"""
Configuration management for embed-postgres
"""

import os
import platform
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class PostgreSQLConfig:
    """Configuration for PostgreSQL embedded instance"""
    
    # Installation settings
    version: str = "17.6"
    install_dir: Optional[str] = None
    data_dir: Optional[str] = None
    
    # Server settings
    port: Optional[int] = None
    host: str = "localhost"
    username: str = "postgres"
    password: str = "password"
    
    # Runtime settings
    timeout: int = 30
    cleanup_on_exit: bool = True
    
    # Process monitoring settings
    enable_monitoring: bool = False
    auto_restart: bool = True
    max_restart_attempts: int = 3
    restart_delay: float = 5.0
    monitoring_interval: float = 1.0
    
    # PostgreSQL configuration
    postgres_config: Dict[str, Any] = field(default_factory=lambda: {
        "shared_preload_libraries": "",
        "max_connections": "100",
        "shared_buffers": "128MB",
        "effective_cache_size": "4GB",
        "maintenance_work_mem": "64MB",
        "checkpoint_completion_target": "0.9",
        "wal_buffers": "16MB",
        "default_statistics_target": "100",
        "random_page_cost": "4.0",
        "effective_io_concurrency": "2",
        "work_mem": "4MB",
        "min_wal_size": "1GB",
        "max_wal_size": "4GB",
    })
    
    def __post_init__(self):
        """Set default directories if not provided"""
        if self.install_dir is None:
            self.install_dir = os.path.join(os.path.expanduser("~"), ".embed-postgres", "install")
        
        if self.data_dir is None:
            self.data_dir = os.path.join(os.path.expanduser("~"), ".embed-postgres", "data")
    
    @property
    def platform(self) -> str:
        """Get the current platform identifier"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "linux":
            if machine in ["x86_64", "amd64"]:
                return "linux-amd64"
            elif machine in ["aarch64", "arm64"]:
                return "linux-arm64"
        elif system == "darwin":
            if machine in ["x86_64", "amd64"]:
                return "darwin-amd64"
            elif machine in ["arm64", "aarch64"]:
                return "darwin-arm64"
        elif system == "windows":
            if machine in ["x86_64", "amd64"]:
                return "windows-amd64"
        
        raise ValueError(f"Unsupported platform: {system}-{machine}")
    
    def get_download_url(self) -> str:
        """Get the download URL for PostgreSQL binaries"""
        base_url = "https://github.com/theseus-rs/postgresql-binaries/releases/download"
        
        # Map our platform names to Rust target triples
        platform_map = {
            "linux-amd64": "x86_64-unknown-linux-gnu",
            "linux-arm64": "aarch64-unknown-linux-gnu", 
            "darwin-amd64": "x86_64-apple-darwin",
            "darwin-arm64": "aarch64-apple-darwin",
            "windows-amd64": "x86_64-pc-windows-msvc"
        }
        
        target = platform_map.get(self.platform)
        if not target:
            raise ValueError(f"No PostgreSQL binary available for platform: {self.platform}")
        
        # Use format: postgresql-{version}-{target}.tar.gz
        # Note: Windows uses .zip, others use .tar.gz
        extension = "zip" if self.platform.startswith("windows") else "tar.gz"
        filename = f"postgresql-{self.version}.0-{target}.{extension}"
        
        return f"{base_url}/{self.version}.0/{filename}"
