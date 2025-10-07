"""
Unit tests for PostgreSQL process monitoring functionality
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from embed_postgres.config import PostgreSQLConfig
from embed_postgres.monitor import ProcessMonitor
from embed_postgres.exceptions import PostgreSQLMonitorError


class TestProcessMonitor(unittest.TestCase):
    """Test ProcessMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = PostgreSQLConfig(
            enable_monitoring=True,
            auto_restart=True,
            max_restart_attempts=2,
            restart_delay=0.1,
            monitoring_interval=0.1
        )
        self.restart_callback = Mock()
        self.monitor = ProcessMonitor(self.config, self.restart_callback)
    
    def test_monitor_initialization(self):
        """Test monitor initialization"""
        self.assertFalse(self.monitor.is_monitoring())
        self.assertEqual(self.monitor.get_restart_count(), 0)
        
        status = self.monitor.get_status()
        self.assertFalse(status['is_monitoring'])
        self.assertEqual(status['restart_count'], 0)
        self.assertTrue(status['auto_restart_enabled'])
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring"""
        process_checker = Mock(return_value=True)
        
        # Start monitoring
        self.monitor.start_monitoring(process_checker)
        self.assertTrue(self.monitor.is_monitoring())
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.is_monitoring())
    
    def test_monitoring_disabled_in_config(self):
        """Test that monitoring doesn't start when disabled in config"""
        config = PostgreSQLConfig(enable_monitoring=False)
        monitor = ProcessMonitor(config, self.restart_callback)
        
        process_checker = Mock(return_value=True)
        monitor.start_monitoring(process_checker)
        
        self.assertFalse(monitor.is_monitoring())
    
    def test_process_death_triggers_restart(self):
        """Test that process death triggers restart callback"""
        # Mock process checker that returns False (process dead)
        process_checker = Mock(return_value=False)
        
        self.monitor.start_monitoring(process_checker)
        
        # Wait for monitoring loop to detect death and restart
        time.sleep(0.2)
        
        # Verify restart was called at least once
        self.restart_callback.assert_called()
        self.assertGreaterEqual(self.monitor.get_restart_count(), 1)
        
        self.monitor.stop_monitoring()
    
    def test_max_restart_attempts_exceeded(self):
        """Test behavior when max restart attempts are exceeded"""
        # Mock process checker that always returns False
        process_checker = Mock(return_value=False)
        
        # Mock restart callback that raises exception to simulate restart failure
        self.restart_callback.side_effect = Exception("Restart failed")
        
        self.monitor.start_monitoring(process_checker)
        
        # Wait for multiple restart attempts
        time.sleep(0.5)
        
        # Should have stopped monitoring after max attempts
        self.assertFalse(self.monitor.is_monitoring())
        self.assertEqual(self.monitor.get_restart_count(), self.config.max_restart_attempts)
    
    def test_reset_restart_count(self):
        """Test resetting restart count"""
        # Simulate some restarts
        self.monitor._restart_count = 2
        
        self.assertEqual(self.monitor.get_restart_count(), 2)
        
        self.monitor.reset_restart_count()
        self.assertEqual(self.monitor.get_restart_count(), 0)
    
    def test_auto_restart_disabled(self):
        """Test behavior when auto-restart is disabled"""
        config = PostgreSQLConfig(
            enable_monitoring=True,
            auto_restart=False,
            monitoring_interval=0.1
        )
        monitor = ProcessMonitor(config, self.restart_callback)
        
        process_checker = Mock(return_value=False)
        monitor.start_monitoring(process_checker)
        
        # Wait for monitoring loop
        time.sleep(0.3)
        
        # Should have stopped monitoring without calling restart
        self.assertFalse(monitor.is_monitoring())
        self.restart_callback.assert_not_called()


class TestPostgreSQLMonitoring(unittest.TestCase):
    """Test PostgreSQL class monitoring integration"""
    
    @patch('embed_postgres.postgresql.PostgreSQLDownloader')
    @patch('embed_postgres.postgresql.subprocess.Popen')
    def test_monitoring_enabled_on_start(self, mock_popen, mock_downloader):
        """Test that monitoring starts when PostgreSQL starts"""
        from embed_postgres.postgresql import PostgreSQL
        
        # Mock successful process
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process running
        mock_popen.return_value = mock_process
        
        # Mock downloader
        mock_downloader_instance = Mock()
        mock_downloader.return_value = mock_downloader_instance
        
        config = PostgreSQLConfig(enable_monitoring=True)
        pg = PostgreSQL(config)
        pg._is_initialized = True  # Skip initialization
        
        with patch.object(pg, '_wait_for_server_start'):
            pg.start()
        
        # Check that monitor was created and started
        self.assertIsNotNone(pg._monitor)
        self.assertTrue(pg._monitor.is_monitoring())
        
        pg.stop()
    
    @patch('embed_postgres.postgresql.PostgreSQLDownloader')
    def test_monitoring_methods(self, mock_downloader):
        """Test monitoring control methods"""
        from embed_postgres.postgresql import PostgreSQL
        
        config = PostgreSQLConfig(enable_monitoring=False)  # Start disabled
        pg = PostgreSQL(config)
        
        # Test getting status when monitoring is disabled
        status = pg.get_monitoring_status()
        self.assertFalse(status['monitoring_enabled'])
        self.assertFalse(status['is_monitoring'])
        
        # Test enabling monitoring when not running (should raise error)
        with self.assertRaises(PostgreSQLMonitorError):
            pg.enable_monitoring()
    
    def test_config_monitoring_options(self):
        """Test monitoring configuration options"""
        config = PostgreSQLConfig(
            enable_monitoring=True,
            auto_restart=False,
            max_restart_attempts=5,
            restart_delay=2.5,
            monitoring_interval=0.8
        )
        
        self.assertTrue(config.enable_monitoring)
        self.assertFalse(config.auto_restart)
        self.assertEqual(config.max_restart_attempts, 5)
        self.assertEqual(config.restart_delay, 2.5)
        self.assertEqual(config.monitoring_interval, 0.8)


if __name__ == '__main__':
    unittest.main()
