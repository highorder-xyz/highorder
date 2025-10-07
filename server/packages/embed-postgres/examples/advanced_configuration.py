"""
Advanced configuration examples for embed-postgres
"""

import tempfile
import os
from pathlib import Path
from embed_postgres import PostgreSQL, PostgreSQLConfig


def custom_data_directory_example():
    """Example using custom data directory"""
    print("=== Custom Data Directory Example ===")
    
    # Create a custom data directory in /tmp
    custom_data_dir = "/tmp/my_postgres_data"
    custom_install_dir = "/tmp/my_postgres_install"
    
    config = PostgreSQLConfig(
        version="17.6",
        data_dir=custom_data_dir,
        install_dir=custom_install_dir,
        cleanup_on_exit=True  # Will cleanup on exit
    )
    
    with PostgreSQL(config) as postgres:
        print(f"PostgreSQL data directory: {postgres.config.data_dir}")
        print(f"PostgreSQL install directory: {postgres.config.install_dir}")
        print(f"PostgreSQL started on port: {postgres.config.port}")
        
        # Create and use a database
        postgres.create_database("custom_location_db")
        print("Created database in custom location")
        
        # Verify the custom directory exists
        if Path(custom_data_dir).exists():
            print(f"Data directory exists: {custom_data_dir}")
            files = list(Path(custom_data_dir).iterdir())
            print(f"Data directory contains {len(files)} items")
        
        postgres.drop_database("custom_location_db")
        print("Dropped database")
    
    print("PostgreSQL stopped and cleaned up")


def no_cleanup_example():
    """Example with cleanup disabled - data persists after exit"""
    print("\n=== No Cleanup Example ===")
    
    persistent_data_dir = "/tmp/persistent_postgres_data"
    
    config = PostgreSQLConfig(
        version="17.6",
        data_dir=persistent_data_dir,
        cleanup_on_exit=False,  # Data will persist after exit
        port=5433  # Use a fixed port
    )
    
    postgres = PostgreSQL(config)
    
    try:
        postgres.setup()
        postgres.start()
        
        print(f"PostgreSQL started on fixed port: {postgres.config.port}")
        print(f"Data directory: {postgres.config.data_dir}")
        print("Cleanup is DISABLED - data will persist after exit")
        
        # Create a persistent database
        postgres.create_database("persistent_db")
        print("Created persistent database")
        
        # Add some data simulation
        url = postgres.get_connection_url("persistent_db")
        print(f"Connection URL: {url}")
        print("Database will remain available after this script exits")
        
    finally:
        postgres.stop()
        print("PostgreSQL stopped but data directory preserved")
        
        # Verify data directory still exists
        if Path(persistent_data_dir).exists():
            print(f"✓ Data directory still exists: {persistent_data_dir}")
        else:
            print("✗ Data directory was removed")


def custom_postgres_settings_example():
    """Example with custom PostgreSQL configuration"""
    print("\n=== Custom PostgreSQL Settings Example ===")
    
    config = PostgreSQLConfig(
        version="17.6",
        cleanup_on_exit=True,
        postgres_config={
            # Memory settings
            "shared_buffers": "256MB",
            "effective_cache_size": "1GB",
            "work_mem": "8MB",
            "maintenance_work_mem": "128MB",
            
            # Connection settings
            "max_connections": "200",
            "max_prepared_transactions": "100",
            
            # Logging settings
            "log_statement": "all",
            "log_min_duration_statement": "1000",  # Log queries > 1 second
            "log_line_prefix": "%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ",
            
            # Performance settings
            "checkpoint_completion_target": "0.9",
            "wal_buffers": "32MB",
            "default_statistics_target": "200",
            
            # Custom settings
            "timezone": "UTC",
            "default_text_search_config": "pg_catalog.english"
        }
    )
    
    with PostgreSQL(config) as postgres:
        print(f"PostgreSQL started with custom configuration on port: {postgres.config.port}")
        
        # Show some configuration
        print("\nCustom PostgreSQL settings applied:")
        for key, value in config.postgres_config.items():
            print(f"  {key} = {value}")
        
        postgres.create_database("configured_db")
        print("\nCreated database with custom configuration")
        
        postgres.drop_database("configured_db")
        print("Dropped database")


def multiple_instances_example():
    """Example running multiple PostgreSQL instances simultaneously"""
    print("\n=== Multiple Instances Example ===")
    
    # Configuration for first instance
    config1 = PostgreSQLConfig(
        version="17.6",
        data_dir="/tmp/postgres_instance_1",
        port=5434,
        cleanup_on_exit=True
    )
    
    # Configuration for second instance  
    config2 = PostgreSQLConfig(
        version="17.6",
        data_dir="/tmp/postgres_instance_2", 
        port=5435,
        cleanup_on_exit=True
    )
    
    postgres1 = PostgreSQL(config1)
    postgres2 = PostgreSQL(config2)
    
    try:
        # Start both instances
        postgres1.setup()
        postgres1.start()
        print(f"Instance 1 started on port: {postgres1.config.port}")
        
        postgres2.setup()
        postgres2.start()
        print(f"Instance 2 started on port: {postgres2.config.port}")
        
        # Create databases on both instances
        postgres1.create_database("instance1_db")
        postgres2.create_database("instance2_db")
        
        print("\nBoth instances running simultaneously:")
        print(f"Instance 1: {postgres1.get_connection_url('instance1_db')}")
        print(f"Instance 2: {postgres2.get_connection_url('instance2_db')}")
        
        # Verify both are running
        print(f"\nInstance 1 running: {postgres1.is_running()}")
        print(f"Instance 2 running: {postgres2.is_running()}")
        
        # Clean up databases
        postgres1.drop_database("instance1_db")
        postgres2.drop_database("instance2_db")
        
    finally:
        postgres1.stop()
        postgres2.stop()
        print("\nBoth instances stopped")


def temporary_directory_example():
    """Example using system temporary directory"""
    print("\n=== Temporary Directory Example ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = PostgreSQLConfig(
            version="17.6",
            data_dir=os.path.join(temp_dir, "postgres_data"),
            install_dir=os.path.join(temp_dir, "postgres_install"),
            cleanup_on_exit=True
        )
        
        with PostgreSQL(config) as postgres:
            print(f"Using temporary directory: {temp_dir}")
            print(f"PostgreSQL started on port: {postgres.config.port}")
            
            postgres.create_database("temp_db")
            print("Created database in temporary location")
            
            # Show directory contents
            data_path = Path(config.data_dir)
            if data_path.exists():
                files = list(data_path.iterdir())
                print(f"Temporary data directory contains {len(files)} items")
            
            postgres.drop_database("temp_db")
            print("Dropped database")
        
        print("PostgreSQL stopped")
    
    print("Temporary directory automatically cleaned up")


if __name__ == "__main__":
    custom_data_directory_example()
    no_cleanup_example()
    custom_postgres_settings_example()
    multiple_instances_example()
    temporary_directory_example()
