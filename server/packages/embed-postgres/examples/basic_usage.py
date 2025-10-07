"""
Basic usage example for embed-postgres
"""

from embed_postgres import PostgreSQL, PostgreSQLConfig


def basic_example():
    """Basic usage with default configuration"""
    print("=== Basic Example ===")
    
    with PostgreSQL() as postgres:
        print(f"PostgreSQL started on port: {postgres.config.port}")
        
        # Create a database
        database_name = "test_db"
        postgres.create_database(database_name)
        print(f"Created database: {database_name}")
        
        # Check if database exists
        exists = postgres.database_exists(database_name)
        print(f"Database '{database_name}' exists: {exists}")
        
        # Get connection URL
        url = postgres.get_connection_url(database_name)
        print(f"Connection URL: {url}")
        
        # Drop database
        postgres.drop_database(database_name)
        print(f"Dropped database: {database_name}")


def custom_config_example():
    """Example with custom configuration"""
    print("\n=== Custom Configuration Example ===")
    
    config = PostgreSQLConfig(
        version="17.6",
        username="postgres",  # Use default postgres user
        password="password",
        postgres_config={
            "max_connections": "50",
            "shared_buffers": "64MB"
        }
    )
    
    postgres = PostgreSQL(config)
    
    try:
        postgres.setup()
        postgres.start()
        
        print(f"PostgreSQL started with custom config on port: {postgres.config.port}")
        
        # Create multiple databases
        databases = ["app_db", "test_db", "dev_db"]
        
        for db_name in databases:
            postgres.create_database(db_name)
            print(f"Created database: {db_name}")
        
        # List all created databases
        print("\nCreated databases:")
        for db_name in databases:
            exists = postgres.database_exists(db_name)
            print(f"  - {db_name}: {'exists' if exists else 'not found'}")
        
        # Cleanup
        for db_name in databases:
            postgres.drop_database(db_name)
            print(f"Dropped database: {db_name}")
            
    finally:
        postgres.stop()


def manual_management_example():
    """Example of manual PostgreSQL management"""
    print("\n=== Manual Management Example ===")
    
    postgres = PostgreSQL()
    
    try:
        print("Setting up PostgreSQL...")
        postgres.setup()
        
        print("Starting PostgreSQL server...")
        postgres.start()
        
        print(f"Server is running: {postgres.is_running()}")
        print(f"Connection URL: {postgres.get_connection_url()}")
        
        # Do some work...
        postgres.create_database("work_db")
        print("Created work database")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Stopping PostgreSQL server...")
        postgres.stop()
        print(f"Server is running: {postgres.is_running()}")


if __name__ == "__main__":
    basic_example()
    custom_config_example()
    manual_management_example()
