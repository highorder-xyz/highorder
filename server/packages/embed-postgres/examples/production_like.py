"""
Production-like examples for embed-postgres
"""

import os
import signal
import time
from pathlib import Path
from embed_postgres import PostgreSQL, PostgreSQLConfig


def production_config_example():
    """Example with production-like configuration"""
    print("=== Production-like Configuration Example ===")
    
    config = PostgreSQLConfig(
        version="17.6",
        data_dir="/tmp/production_postgres",
        cleanup_on_exit=False,  # Don't cleanup in production
        timeout=60,  # Longer timeout for production
        postgres_config={
            # Production memory settings
            "shared_buffers": "512MB",
            "effective_cache_size": "2GB",
            "work_mem": "16MB",
            "maintenance_work_mem": "256MB",
            "wal_buffers": "64MB",
            
            # Connection settings
            "max_connections": "100",
            "max_prepared_transactions": "50",
            
            # Performance tuning
            "random_page_cost": "1.1",  # For SSD
            "effective_io_concurrency": "200",  # For SSD
            "checkpoint_completion_target": "0.9",
            "checkpoint_timeout": "15min",
            
            # WAL settings
            "wal_level": "replica",
            "max_wal_size": "2GB",
            "min_wal_size": "512MB",
            
            # Logging for production
            "log_destination": "stderr",
            "log_statement": "mod",  # Log modifications
            "log_min_duration_statement": "5000",  # Log slow queries
            "log_checkpoints": "on",
            "log_connections": "on",
            "log_disconnections": "on",
            "log_lock_waits": "on",
            
            # Autovacuum tuning
            "autovacuum_max_workers": "4",
            "autovacuum_naptime": "30s",
            "autovacuum_vacuum_cost_limit": "2000",
            
            # Security
            "ssl": "off",  # Would be 'on' in real production
            "password_encryption": "scram-sha-256"
        }
    )
    
    postgres = PostgreSQL(config)
    
    try:
        postgres.setup()
        postgres.start()
        
        print(f"Production PostgreSQL started on port: {postgres.config.port}")
        print(f"Data directory: {postgres.config.data_dir}")
        print("Configuration optimized for production workload")
        
        # Create application database
        postgres.create_database("app_production")
        print("Created production database")
        
        url = postgres.get_connection_url("app_production")
        print(f"Production connection URL: {url}")
        
        print("\nProduction features enabled:")
        print("- Persistent data (cleanup_on_exit=False)")
        print("- Optimized memory settings")
        print("- Query logging for slow queries (>5s)")
        print("- Connection logging")
        print("- Checkpoint logging")
        
        # Simulate keeping it running
        print("\nPostgreSQL is running in production mode...")
        print("Data will persist after script exit")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # In production, you might not want to stop automatically
        choice = input("\nStop PostgreSQL? (y/N): ").lower()
        if choice == 'y':
            postgres.stop()
            print("PostgreSQL stopped")
        else:
            print("PostgreSQL left running")
            print(f"To stop later: kill {postgres.process.pid if postgres.process else 'N/A'}")


def development_with_persistence_example():
    """Example for development with data persistence"""
    print("\n=== Development with Persistence Example ===")
    
    dev_data_dir = os.path.expanduser("~/dev_postgres_data")
    
    config = PostgreSQLConfig(
        version="17.6",
        data_dir=dev_data_dir,
        cleanup_on_exit=False,  # Keep data between development sessions
        postgres_config={
            # Development-friendly settings
            "shared_buffers": "128MB",
            "work_mem": "4MB",
            "max_connections": "50",
            
            # Detailed logging for development
            "log_statement": "all",
            "log_min_duration_statement": "0",  # Log all queries
            "log_line_prefix": "%t [%p]: [%l-1] user=%u,db=%d ",
            
            # Fast checkpoints for development
            "checkpoint_timeout": "5min",
            "checkpoint_completion_target": "0.7",
            
            # Disable some production features for speed
            "fsync": "off",  # Faster but less safe
            "synchronous_commit": "off",
            "full_page_writes": "off"
        }
    )
    
    postgres = PostgreSQL(config)
    
    try:
        postgres.setup()
        postgres.start()
        
        print(f"Development PostgreSQL started on port: {postgres.config.port}")
        print(f"Persistent data directory: {dev_data_dir}")
        
        # Check if we have existing databases
        existing_dbs = []
        test_dbs = ["dev_app", "test_db", "staging_db"]
        
        for db_name in test_dbs:
            if postgres.database_exists(db_name):
                existing_dbs.append(db_name)
        
        if existing_dbs:
            print(f"Found existing databases: {existing_dbs}")
        else:
            print("No existing databases found, creating development databases...")
            for db_name in test_dbs:
                postgres.create_database(db_name)
                print(f"Created {db_name}")
        
        print("\nDevelopment features:")
        print("- All queries logged")
        print("- Fast checkpoints")
        print("- Reduced durability for speed")
        print("- Data persists between sessions")
        
        # Show connection URLs
        print("\nConnection URLs:")
        for db_name in test_dbs:
            if postgres.database_exists(db_name):
                url = postgres.get_connection_url(db_name)
                print(f"  {db_name}: {url}")
        
    finally:
        postgres.stop()
        print(f"\nDevelopment PostgreSQL stopped")
        print(f"Data preserved in: {dev_data_dir}")


def testing_isolated_example():
    """Example for testing with isolated instances"""
    print("\n=== Testing with Isolation Example ===")
    
    import tempfile
    import uuid
    
    # Create unique test instance
    test_id = str(uuid.uuid4())[:8]
    
    with tempfile.TemporaryDirectory(prefix=f"test_postgres_{test_id}_") as temp_dir:
        config = PostgreSQLConfig(
            version="17.6",
            data_dir=os.path.join(temp_dir, "data"),
            cleanup_on_exit=True,  # Always cleanup after tests
            postgres_config={
                # Fast settings for testing
                "shared_buffers": "32MB",
                "work_mem": "2MB",
                "max_connections": "20",
                "fsync": "off",
                "synchronous_commit": "off",
                "checkpoint_timeout": "1min",
                
                # Minimal logging for tests
                "log_statement": "none",
                "log_min_duration_statement": "-1"
            }
        )
        
        with PostgreSQL(config) as postgres:
            print(f"Test PostgreSQL instance {test_id} started on port: {postgres.config.port}")
            print(f"Isolated test directory: {temp_dir}")
            
            # Create test databases
            test_databases = [f"test_db_{i}" for i in range(3)]
            
            for db_name in test_databases:
                postgres.create_database(db_name)
                print(f"Created test database: {db_name}")
            
            # Simulate test operations
            print("\nRunning isolated tests...")
            for i, db_name in enumerate(test_databases):
                url = postgres.get_connection_url(db_name)
                print(f"Test {i+1}: {url}")
                # Here you would run your actual tests
            
            print("All tests completed")
            
            # Cleanup test databases
            for db_name in test_databases:
                postgres.drop_database(db_name)
                print(f"Cleaned up: {db_name}")
        
        print(f"Test instance {test_id} stopped and cleaned up")


def monitoring_example():
    """Example with monitoring and health checks"""
    print("\n=== Monitoring Example ===")
    
    config = PostgreSQLConfig(
        version="17.6",
        cleanup_on_exit=True,
        postgres_config={
            "shared_buffers": "128MB",
            "max_connections": "50",
            
            # Enable statistics collection
            "track_activities": "on",
            "track_counts": "on",
            "track_io_timing": "on",
            "track_functions": "all",
            
            # Logging for monitoring
            "log_checkpoints": "on",
            "log_connections": "on",
            "log_disconnections": "on",
            "log_min_duration_statement": "1000"
        }
    )
    
    with PostgreSQL(config) as postgres:
        print(f"Monitored PostgreSQL started on port: {postgres.config.port}")
        
        postgres.create_database("monitored_db")
        
        # Basic health checks
        print("\nHealth Checks:")
        print(f"✓ PostgreSQL is running: {postgres.is_running()}")
        print(f"✓ Database exists: {postgres.database_exists('monitored_db')}")
        
        # Connection test
        try:
            url = postgres.get_connection_url("monitored_db")
            print(f"✓ Connection URL available: {url}")
        except Exception as e:
            print(f"✗ Connection test failed: {e}")
        
        print("\nMonitoring features enabled:")
        print("- Activity tracking")
        print("- I/O timing statistics")
        print("- Function call statistics")
        print("- Connection logging")
        print("- Slow query logging (>1s)")
        
        postgres.drop_database("monitored_db")
        print("\nMonitoring example completed")


if __name__ == "__main__":
    production_config_example()
    development_with_persistence_example()
    testing_isolated_example()
    monitoring_example()
