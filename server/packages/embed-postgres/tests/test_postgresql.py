"""
Tests for PostgreSQL embedded functionality
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from embed_postgres import PostgreSQL, PostgreSQLConfig
from embed_postgres.exceptions import (
    PostgreSQLInstallError,
    PostgreSQLStartError,
    PostgreSQLDatabaseError
)


class TestPostgreSQL:
    """Test PostgreSQL embedded functionality"""
    
    @pytest.fixture
    def temp_config(self):
        """Create a temporary configuration for testing"""
        temp_dir = tempfile.mkdtemp()
        config = PostgreSQLConfig(
            install_dir=str(Path(temp_dir) / "install"),
            data_dir=str(Path(temp_dir) / "data"),
            cleanup_on_exit=False
        )
        yield config
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_init(self, temp_config):
        """Test PostgreSQL initialization"""
        postgres = PostgreSQL(temp_config)
        
        assert postgres.config == temp_config
        assert postgres.process is None
        assert not postgres._is_initialized
    
    def test_init_with_default_config(self):
        """Test PostgreSQL initialization with default config"""
        postgres = PostgreSQL()
        
        assert postgres.config is not None
        assert isinstance(postgres.config, PostgreSQLConfig)
    
    @patch('embed_postgres.postgresql.PostgreSQLDownloader')
    def test_setup_calls_downloader(self, mock_downloader_class, temp_config):
        """Test that setup calls the downloader"""
        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader
        
        postgres = PostgreSQL(temp_config)
        
        with patch.object(postgres, '_initialize_database'):
            postgres.setup()
        
        mock_downloader.download_and_install.assert_called_once()
    
    def test_is_running_false_when_no_process(self, temp_config):
        """Test is_running returns False when no process"""
        postgres = PostgreSQL(temp_config)
        assert not postgres.is_running()
    
    @patch('embed_postgres.postgresql.subprocess.Popen')
    def test_is_running_true_when_process_alive(self, mock_popen, temp_config):
        """Test is_running returns True when process is alive"""
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process
        
        postgres = PostgreSQL(temp_config)
        postgres.process = mock_process
        
        assert postgres.is_running()
    
    @patch('embed_postgres.postgresql.subprocess.Popen')
    def test_is_running_false_when_process_dead(self, mock_popen, temp_config):
        """Test is_running returns False when process is dead"""
        mock_process = Mock()
        mock_process.poll.return_value = 1  # Process has exited
        mock_popen.return_value = mock_process
        
        postgres = PostgreSQL(temp_config)
        postgres.process = mock_process
        
        assert not postgres.is_running()
    
    def test_get_connection_url(self, temp_config):
        """Test connection URL generation"""
        temp_config.port = 5432
        postgres = PostgreSQL(temp_config)
        
        url = postgres.get_connection_url("test_db")
        expected = f"postgresql://{temp_config.username}:{temp_config.password}@{temp_config.host}:5432/test_db"
        
        assert url == expected
    
    def test_get_connection_url_default_database(self, temp_config):
        """Test connection URL with default database"""
        temp_config.port = 5432
        postgres = PostgreSQL(temp_config)
        
        url = postgres.get_connection_url()
        expected = f"postgresql://{temp_config.username}:{temp_config.password}@{temp_config.host}:5432/postgres"
        
        assert url == expected
    
    @patch('embed_postgres.postgresql.socket.socket')
    def test_find_free_port(self, mock_socket, temp_config):
        """Test finding a free port"""
        mock_sock = Mock()
        mock_sock.getsockname.return_value = ('localhost', 12345)
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        postgres = PostgreSQL(temp_config)
        port = postgres._find_free_port()
        
        assert port == 12345
    
    def test_context_manager_setup_and_cleanup(self, temp_config):
        """Test context manager calls setup and cleanup"""
        postgres = PostgreSQL(temp_config)
        
        with patch.object(postgres, 'setup') as mock_setup, \
             patch.object(postgres, 'start') as mock_start, \
             patch.object(postgres, 'stop') as mock_stop:
            
            with postgres:
                pass
            
            mock_setup.assert_called_once()
            mock_start.assert_called_once()
            mock_stop.assert_called_once()
    
    @patch('embed_postgres.postgresql.subprocess.run')
    def test_database_exists_true(self, mock_run, temp_config):
        """Test database_exists returns True when database exists"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "1\n"
        
        postgres = PostgreSQL(temp_config)
        postgres.process = Mock()  # Simulate running process
        
        with patch.object(postgres, 'is_running', return_value=True):
            result = postgres.database_exists("test_db")
        
        assert result is True
    
    @patch('embed_postgres.postgresql.subprocess.run')
    def test_database_exists_false(self, mock_run, temp_config):
        """Test database_exists returns False when database doesn't exist"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "\n"
        
        postgres = PostgreSQL(temp_config)
        postgres.process = Mock()  # Simulate running process
        
        with patch.object(postgres, 'is_running', return_value=True):
            result = postgres.database_exists("test_db")
        
        assert result is False
    
    def test_database_exists_not_running_raises_error(self, temp_config):
        """Test database_exists raises error when server not running"""
        postgres = PostgreSQL(temp_config)
        
        with pytest.raises(PostgreSQLDatabaseError, match="PostgreSQL server is not running"):
            postgres.database_exists("test_db")
    
    @patch('embed_postgres.postgresql.subprocess.run')
    def test_create_database_success(self, mock_run, temp_config):
        """Test successful database creation"""
        mock_run.return_value.returncode = 0
        
        postgres = PostgreSQL(temp_config)
        postgres.process = Mock()  # Simulate running process
        
        with patch.object(postgres, 'is_running', return_value=True):
            postgres.create_database("test_db")
        
        mock_run.assert_called_once()
    
    @patch('embed_postgres.postgresql.subprocess.run')
    def test_create_database_failure(self, mock_run, temp_config):
        """Test database creation failure"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Database already exists"
        
        postgres = PostgreSQL(temp_config)
        postgres.process = Mock()  # Simulate running process
        
        with patch.object(postgres, 'is_running', return_value=True):
            with pytest.raises(PostgreSQLDatabaseError, match="Failed to create database"):
                postgres.create_database("test_db")
    
    def test_create_database_not_running_raises_error(self, temp_config):
        """Test create_database raises error when server not running"""
        postgres = PostgreSQL(temp_config)
        
        with pytest.raises(PostgreSQLDatabaseError, match="PostgreSQL server is not running"):
            postgres.create_database("test_db")
    
    @patch('embed_postgres.postgresql.subprocess.run')
    def test_drop_database_success(self, mock_run, temp_config):
        """Test successful database drop"""
        mock_run.return_value.returncode = 0
        
        postgres = PostgreSQL(temp_config)
        postgres.process = Mock()  # Simulate running process
        
        with patch.object(postgres, 'is_running', return_value=True):
            postgres.drop_database("test_db")
        
        mock_run.assert_called_once()
    
    def test_drop_database_not_running_raises_error(self, temp_config):
        """Test drop_database raises error when server not running"""
        postgres = PostgreSQL(temp_config)
        
        with pytest.raises(PostgreSQLDatabaseError, match="PostgreSQL server is not running"):
            postgres.drop_database("test_db")
