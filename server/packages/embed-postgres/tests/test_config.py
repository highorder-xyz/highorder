"""
Tests for PostgreSQL configuration
"""

import pytest
import platform
from embed_postgres.config import PostgreSQLConfig


class TestPostgreSQLConfig:
    """Test PostgreSQL configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = PostgreSQLConfig()
        
        assert config.version == "15.4"
        assert config.host == "localhost"
        assert config.username == "postgres"
        assert config.password == "password"
        assert config.port is None
        assert config.timeout == 30
        assert config.cleanup_on_exit is True
        assert config.install_dir is not None
        assert config.data_dir is not None
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = PostgreSQLConfig(
            version="14.9",
            port=5433,
            username="testuser",
            password="testpass",
            timeout=60
        )
        
        assert config.version == "14.9"
        assert config.port == 5433
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.timeout == 60
    
    def test_platform_detection(self):
        """Test platform detection"""
        config = PostgreSQLConfig()
        platform_str = config.platform
        
        # Should return a valid platform string
        valid_platforms = [
            "linux-amd64", "linux-arm64",
            "darwin-amd64", "darwin-arm64",
            "windows-amd64"
        ]
        assert platform_str in valid_platforms
    
    def test_download_url_generation(self):
        """Test download URL generation"""
        config = PostgreSQLConfig(version="15.4")
        url = config.get_download_url()
        
        assert url.startswith("https://get.enterprisedb.com/postgresql/")
        assert "postgresql-15.4" in url
        assert url.endswith((".tar.gz", ".zip"))
    
    def test_postgres_config_defaults(self):
        """Test default PostgreSQL configuration"""
        config = PostgreSQLConfig()
        
        assert "max_connections" in config.postgres_config
        assert "shared_buffers" in config.postgres_config
        assert config.postgres_config["max_connections"] == "100"
        assert config.postgres_config["shared_buffers"] == "128MB"
    
    def test_custom_postgres_config(self):
        """Test custom PostgreSQL configuration"""
        custom_config = {
            "max_connections": "200",
            "shared_buffers": "256MB",
            "custom_setting": "custom_value"
        }
        
        config = PostgreSQLConfig(postgres_config=custom_config)
        
        assert config.postgres_config["max_connections"] == "200"
        assert config.postgres_config["shared_buffers"] == "256MB"
        assert config.postgres_config["custom_setting"] == "custom_value"
