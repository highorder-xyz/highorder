"""
Version management and migration examples for embed-postgres
"""

import os
from pathlib import Path
from embed_postgres import PostgreSQL, PostgreSQLConfig


def different_versions_example():
    """Example using different PostgreSQL versions"""
    print("=== Different PostgreSQL Versions Example ===")
    
    # Test with different versions (if available)
    versions = ["17.6", "16.10", "15.14"]  # Available versions from theseus-rs/postgresql-binaries
    
    for version in versions:
        print(f"\n--- Testing PostgreSQL {version} ---")
        
        config = PostgreSQLConfig(
            version=version,
            data_dir=f"/tmp/postgres_v{version.replace('.', '_')}_data",
            cleanup_on_exit=True
        )
        
        try:
            with PostgreSQL(config) as postgres:
                print(f"PostgreSQL {version} started on port: {postgres.config.port}")
                
                # Create version-specific database
                db_name = f"version_{version.replace('.', '_')}_db"
                postgres.create_database(db_name)
                print(f"Created database: {db_name}")
                
                url = postgres.get_connection_url(db_name)
                print(f"Connection URL: {url}")
                
                postgres.drop_database(db_name)
                print(f"Cleaned up database: {db_name}")
                
        except Exception as e:
            print(f"Error with PostgreSQL {version}: {e}")
            print("This version might not be available for download")


def data_directory_persistence_example():
    """Example showing data directory persistence across restarts"""
    print("\n=== Data Directory Persistence Example ===")
    
    persistent_dir = "/tmp/persistent_postgres_example"
    
    config = PostgreSQLConfig(
        version="17.6",
        data_dir=persistent_dir,
        cleanup_on_exit=False  # Keep data between runs
    )
    
    # First run - create data
    print("--- First Run: Creating persistent data ---")
    postgres1 = PostgreSQL(config)
    
    try:
        postgres1.setup()
        postgres1.start()
        
        print(f"PostgreSQL started on port: {postgres1.config.port}")
        print(f"Data directory: {persistent_dir}")
        
        # Create databases and simulate data
        databases = ["users_db", "products_db", "orders_db"]
        for db_name in databases:
            postgres1.create_database(db_name)
            print(f"Created persistent database: {db_name}")
        
        print("Data created and will persist after shutdown")
        
    finally:
        postgres1.stop()
        print("First instance stopped, data preserved")
    
    # Second run - reuse existing data
    print("\n--- Second Run: Reusing persistent data ---")
    postgres2 = PostgreSQL(config)
    
    try:
        postgres2.setup()  # Will skip initialization if data exists
        postgres2.start()
        
        print(f"PostgreSQL restarted on port: {postgres2.config.port}")
        
        # Check if our databases still exist
        print("Checking for persistent databases:")
        for db_name in databases:
            exists = postgres2.database_exists(db_name)
            status = "✓ Found" if exists else "✗ Missing"
            print(f"  {db_name}: {status}")
        
        print("Successfully reused persistent data!")
        
        # Cleanup for demo
        for db_name in databases:
            if postgres2.database_exists(db_name):
                postgres2.drop_database(db_name)
                print(f"Cleaned up: {db_name}")
        
    finally:
        postgres2.stop()
        print("Second instance stopped")
    
    # Cleanup the persistent directory
    import shutil
    if Path(persistent_dir).exists():
        shutil.rmtree(persistent_dir)
        print(f"Cleaned up persistent directory: {persistent_dir}")


def custom_install_locations_example():
    """Example with custom installation locations"""
    print("\n=== Custom Installation Locations Example ===")
    
    # Different custom locations
    locations = [
        {
            "name": "Home Directory",
            "install_dir": os.path.expanduser("~/my_postgres_install"),
            "data_dir": os.path.expanduser("~/my_postgres_data")
        },
        {
            "name": "Project Directory", 
            "install_dir": "/tmp/project_postgres/install",
            "data_dir": "/tmp/project_postgres/data"
        },
        {
            "name": "System Temp",
            "install_dir": "/tmp/system_postgres_install",
            "data_dir": "/tmp/system_postgres_data"
        }
    ]
    
    for location in locations:
        print(f"\n--- {location['name']} ---")
        
        config = PostgreSQLConfig(
            version="17.6",
            install_dir=location["install_dir"],
            data_dir=location["data_dir"],
            cleanup_on_exit=True
        )
        
        try:
            with PostgreSQL(config) as postgres:
                print(f"Install directory: {postgres.config.install_dir}")
                print(f"Data directory: {postgres.config.data_dir}")
                print(f"Started on port: {postgres.config.port}")
                
                # Verify directories exist
                install_path = Path(postgres.config.install_dir)
                data_path = Path(postgres.config.data_dir)
                
                print(f"Install directory exists: {install_path.exists()}")
                print(f"Data directory exists: {data_path.exists()}")
                
                # Create a test database
                postgres.create_database("location_test_db")
                print("Created test database in custom location")
                
                postgres.drop_database("location_test_db")
                print("Cleaned up test database")
                
        except Exception as e:
            print(f"Error with {location['name']}: {e}")


def no_cleanup_production_simulation():
    """Simulate production environment with no cleanup"""
    print("\n=== Production Simulation (No Cleanup) ===")
    
    production_base = "/tmp/production_simulation"
    
    config = PostgreSQLConfig(
        version="17.6",
        install_dir=f"{production_base}/postgres_install",
        data_dir=f"{production_base}/postgres_data",
        cleanup_on_exit=False,  # Production-like: no cleanup
        postgres_config={
            # Production-like settings
            "shared_buffers": "256MB",
            "max_connections": "100",
            "log_statement": "mod",
            "log_min_duration_statement": "5000"
        }
    )
    
    postgres = PostgreSQL(config)
    
    try:
        postgres.setup()
        postgres.start()
        
        print(f"Production simulation started on port: {postgres.config.port}")
        print(f"Install directory: {config.install_dir}")
        print(f"Data directory: {config.data_dir}")
        print("Cleanup is DISABLED - simulating production environment")
        
        # Create production-like databases
        prod_databases = ["app_production", "app_staging", "analytics"]
        
        for db_name in prod_databases:
            postgres.create_database(db_name)
            print(f"Created production database: {db_name}")
        
        print("\nProduction databases created:")
        for db_name in prod_databases:
            url = postgres.get_connection_url(db_name)
            print(f"  {db_name}: {url}")
        
        print("\nIn production, these databases would persist indefinitely")
        print("Manual cleanup would be required when no longer needed")
        
        # Show what would persist
        install_path = Path(config.install_dir)
        data_path = Path(config.data_dir)
        
        if install_path.exists():
            install_size = sum(f.stat().st_size for f in install_path.rglob('*') if f.is_file())
            print(f"Install directory size: {install_size / 1024 / 1024:.1f} MB")
        
        if data_path.exists():
            data_size = sum(f.stat().st_size for f in data_path.rglob('*') if f.is_file())
            print(f"Data directory size: {data_size / 1024 / 1024:.1f} MB")
        
    finally:
        postgres.stop()
        print("\nProduction simulation stopped")
        print("Data and installation files preserved (cleanup_on_exit=False)")
        
        # In a real production environment, you wouldn't clean up here
        # But for demo purposes, let's clean up
        cleanup = input("Clean up simulation files? (y/N): ").lower()
        if cleanup == 'y':
            import shutil
            if Path(production_base).exists():
                shutil.rmtree(production_base)
                print(f"Cleaned up: {production_base}")
        else:
            print(f"Files preserved at: {production_base}")


if __name__ == "__main__":
    different_versions_example()
    data_directory_persistence_example()
    custom_install_locations_example()
    no_cleanup_production_simulation()
