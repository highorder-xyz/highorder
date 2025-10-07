"""
Process monitoring for PostgreSQL embedded instance
"""

import threading
import time
import logging
from typing import Optional, Callable, Any
from datetime import datetime

from .config import PostgreSQLConfig
from .exceptions import PostgreSQLMonitorError


logger = logging.getLogger(__name__)


class ProcessMonitor:
    """Monitor PostgreSQL process and handle automatic restarts"""
    
    def __init__(self, config: PostgreSQLConfig, restart_callback: Callable[[], None]):
        self.config = config
        self.restart_callback = restart_callback
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._restart_count = 0
        self._last_restart_time: Optional[datetime] = None
        self._is_monitoring = False
        
    def start_monitoring(self, process_checker: Callable[[], bool]) -> None:
        """Start monitoring the PostgreSQL process"""
        if self._is_monitoring:
            logger.warning("Process monitoring is already running")
            return
            
        if not self.config.enable_monitoring:
            logger.info("Process monitoring is disabled in configuration")
            return
            
        self._stop_event.clear()
        self._is_monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(process_checker,),
            daemon=True,
            name="PostgreSQL-Monitor"
        )
        self._monitor_thread.start()
        logger.info("Started PostgreSQL process monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring the PostgreSQL process"""
        if not self._is_monitoring:
            return
            
        self._stop_event.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        
        self._is_monitoring = False
        logger.info("Stopped PostgreSQL process monitoring")
    
    def reset_restart_count(self) -> None:
        """Reset the restart attempt counter"""
        self._restart_count = 0
        self._last_restart_time = None
        logger.debug("Reset restart attempt counter")
    
    def get_restart_count(self) -> int:
        """Get current restart attempt count"""
        return self._restart_count
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is currently active"""
        return self._is_monitoring
    
    def _monitor_loop(self, process_checker: Callable[[], bool]) -> None:
        """Main monitoring loop running in separate thread"""
        logger.debug("Process monitoring loop started")
        
        while not self._stop_event.is_set():
            try:
                # Check if process is still running
                if not process_checker():
                    logger.warning("PostgreSQL process has died unexpectedly")
                    
                    if self.config.auto_restart:
                        self._handle_process_death()
                    else:
                        logger.error("Auto-restart is disabled, stopping monitoring")
                        self._stop_monitoring_internal()
                        break
                
                # Wait for next check
                self._stop_event.wait(self.config.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                # Continue monitoring even if there's an error
                self._stop_event.wait(self.config.monitoring_interval)
        
        logger.debug("Process monitoring loop stopped")
    
    def _handle_process_death(self) -> None:
        """Handle PostgreSQL process death and attempt restart"""
        current_time = datetime.now()
        
        # Check if we've exceeded maximum restart attempts
        if self._restart_count >= self.config.max_restart_attempts:
            logger.error(
                f"Maximum restart attempts ({self.config.max_restart_attempts}) exceeded. "
                "Stopping automatic restart attempts."
            )
            self._stop_monitoring_internal()
            return
        
        self._restart_count += 1
        self._last_restart_time = current_time
        
        logger.info(
            f"Attempting to restart PostgreSQL (attempt {self._restart_count}/"
            f"{self.config.max_restart_attempts})"
        )
        
        try:
            # Wait before restart attempt
            if self.config.restart_delay > 0:
                logger.debug(f"Waiting {self.config.restart_delay} seconds before restart")
                self._stop_event.wait(self.config.restart_delay)
                
                # Check if monitoring was stopped during delay
                if self._stop_event.is_set():
                    return
            
            # Attempt to restart PostgreSQL
            self.restart_callback()
            logger.info(f"Successfully restarted PostgreSQL (attempt {self._restart_count})")
            
        except Exception as e:
            logger.error(f"Failed to restart PostgreSQL (attempt {self._restart_count}): {e}")
            
            # If this was the last attempt, stop monitoring
            if self._restart_count >= self.config.max_restart_attempts:
                self._stop_monitoring_internal()
    
    def _stop_monitoring_internal(self) -> None:
        """Internal method to stop monitoring without joining thread"""
        self._stop_event.set()
        self._is_monitoring = False
        logger.info("Stopped PostgreSQL process monitoring (internal)")
    
    def get_status(self) -> dict:
        """Get current monitoring status"""
        return {
            "is_monitoring": self._is_monitoring,
            "restart_count": self._restart_count,
            "last_restart_time": self._last_restart_time.isoformat() if self._last_restart_time else None,
            "max_restart_attempts": self.config.max_restart_attempts,
            "monitoring_enabled": self.config.enable_monitoring,
            "auto_restart_enabled": self.config.auto_restart
        }
