#!/usr/bin/env python3
"""
Example demonstrating PostgreSQL process monitoring and auto-restart functionality.

This example shows how to:
1. Enable process monitoring with custom configuration
2. Simulate process crashes and observe auto-restart behavior
3. Monitor restart attempts and status
4. Handle monitoring events and errors
"""

import time
import logging
import signal
import os
from embed_postgres import PostgreSQL, PostgreSQLConfig

# Configure logging to see monitoring events
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Create configuration with monitoring enabled
    config = PostgreSQLConfig(
        # Enable process monitoring
        enable_monitoring=True,
        auto_restart=True,
        max_restart_attempts=3,
        restart_delay=2.0,  # Wait 2 seconds before restart
        monitoring_interval=0.5,  # Check every 0.5 seconds
        
        # Other settings
        port=5432,
        cleanup_on_exit=True
    )
    
    print("=== PostgreSQL Process Monitoring Demo ===\n")
    
    # Create PostgreSQL instance
    pg = PostgreSQL(config)
    
    try:
        print("1. Setting up and starting PostgreSQL...")
        pg.setup()
        pg.start()
        
        print(f"✓ PostgreSQL started on port {pg.config.port}")
        print(f"✓ Process monitoring enabled: {config.enable_monitoring}")
        
        # Show initial monitoring status
        status = pg.get_monitoring_status()
        print(f"\nMonitoring Status:")
        print(f"  - Is monitoring: {status['is_monitoring']}")
        print(f"  - Auto-restart: {status['auto_restart_enabled']}")
        print(f"  - Max attempts: {status['max_restart_attempts']}")
        print(f"  - Restart count: {status['restart_count']}")
        
        # Create a test database
        print("\n2. Creating test database...")
        pg.create_database("test_monitoring")
        print("✓ Test database created")
        
        # Simulate normal operation
        print("\n3. Simulating normal operation for 5 seconds...")
        for i in range(5):
            print(f"  - PostgreSQL running: {pg.is_running()}")
            time.sleep(1)
        
        # Simulate process crash by killing the PostgreSQL process
        print("\n4. Simulating process crash...")
        if pg.process:
            print(f"  - Killing PostgreSQL process (PID: {pg.process.pid})")
            pg.process.kill()  # Force kill to simulate crash
            pg.process.wait()
            
        # Wait and observe auto-restart behavior
        print("\n5. Observing auto-restart behavior...")
        for i in range(15):  # Wait up to 15 seconds
            status = pg.get_monitoring_status()
            is_running = pg.is_running()
            
            print(f"  - Time: {i+1}s | Running: {is_running} | Restarts: {status['restart_count']}")
            
            if is_running and status['restart_count'] > 0:
                print("  ✓ PostgreSQL successfully restarted!")
                break
                
            time.sleep(1)
        
        # Verify database still exists after restart
        if pg.is_running():
            print("\n6. Verifying database integrity after restart...")
            exists = pg.database_exists("test_monitoring")
            print(f"  - Test database exists: {exists}")
            
            if exists:
                print("  ✓ Database integrity maintained after restart")
        
        # Show final monitoring status
        print("\n7. Final monitoring status:")
        final_status = pg.get_monitoring_status()
        for key, value in final_status.items():
            print(f"  - {key}: {value}")
        
        # Demonstrate manual monitoring control
        print("\n8. Demonstrating manual monitoring control...")
        print("  - Disabling monitoring...")
        pg.disable_monitoring()
        
        status = pg.get_monitoring_status()
        print(f"  - Monitoring active: {status['is_monitoring']}")
        
        print("  - Re-enabling monitoring...")
        pg.enable_monitoring()
        
        status = pg.get_monitoring_status()
        print(f"  - Monitoring active: {status['is_monitoring']}")
        
        # Reset restart counter
        print("  - Resetting restart counter...")
        pg.reset_restart_count()
        
        status = pg.get_monitoring_status()
        print(f"  - Restart count after reset: {status['restart_count']}")
        
        print("\n✓ Process monitoring demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        
    finally:
        print("\n9. Cleaning up...")
        try:
            if pg.database_exists("test_monitoring"):
                pg.drop_database("test_monitoring")
                print("  ✓ Test database dropped")
        except:
            pass
        
        pg.stop()
        print("  ✓ PostgreSQL stopped")


def demonstrate_crash_resilience():
    """
    Demonstrate how the monitoring system handles multiple crashes
    """
    print("\n=== Crash Resilience Test ===")
    
    config = PostgreSQLConfig(
        enable_monitoring=True,
        auto_restart=True,
        max_restart_attempts=2,  # Lower limit for demo
        restart_delay=1.0,
        monitoring_interval=0.3
    )
    
    pg = PostgreSQL(config)
    
    try:
        pg.setup()
        pg.start()
        print("PostgreSQL started for crash test")
        
        # Simulate multiple crashes
        for crash_num in range(3):  # Try to crash more than max_restart_attempts
            print(f"\nCrash #{crash_num + 1}:")
            
            if pg.process:
                print(f"  - Killing process (PID: {pg.process.pid})")
                pg.process.kill()
                pg.process.wait()
            
            # Wait for restart attempt or failure
            time.sleep(3)
            
            status = pg.get_monitoring_status()
            print(f"  - Restart attempts: {status['restart_count']}")
            print(f"  - Still monitoring: {status['is_monitoring']}")
            print(f"  - PostgreSQL running: {pg.is_running()}")
            
            if not status['is_monitoring']:
                print("  ⚠️  Monitoring stopped (max attempts reached)")
                break
        
    except Exception as e:
        print(f"Expected behavior - monitoring stopped: {e}")
    
    finally:
        pg.stop()
        print("Crash test cleanup completed")


if __name__ == "__main__":
    main()
    
    # Uncomment to run crash resilience test
    # demonstrate_crash_resilience()
