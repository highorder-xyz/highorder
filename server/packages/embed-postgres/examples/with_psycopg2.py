"""
Example using embed-postgres with psycopg2
"""

import sys
from embed_postgres import PostgreSQL

# Check if psycopg2 is available
try:
    import psycopg2
    from psycopg2 import sql
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    print("psycopg2 not installed. Install with: pip install psycopg2-binary")


def psycopg2_example():
    """Example using PostgreSQL with psycopg2"""
    if not HAS_PSYCOPG2:
        print("Skipping psycopg2 example - psycopg2 not available")
        return
    
    print("=== psycopg2 Integration Example ===")
    
    with PostgreSQL() as postgres:
        # Create a database
        database_name = "example_db"
        postgres.create_database(database_name)
        
        # Get connection URL
        connection_url = postgres.get_connection_url(database_name)
        print(f"Connecting to: {connection_url}")
        
        # Connect using psycopg2
        conn = psycopg2.connect(connection_url)
        cursor = conn.cursor()
        
        try:
            # Create a table
            cursor.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created 'users' table")
            
            # Insert some data
            users_data = [
                ("Alice Johnson", "alice@example.com"),
                ("Bob Smith", "bob@example.com"),
                ("Charlie Brown", "charlie@example.com")
            ]
            
            cursor.executemany(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                users_data
            )
            conn.commit()
            print(f"Inserted {len(users_data)} users")
            
            # Query data
            cursor.execute("SELECT id, name, email FROM users ORDER BY id")
            users = cursor.fetchall()
            
            print("\nUsers in database:")
            for user_id, name, email in users:
                print(f"  {user_id}: {name} ({email})")
            
            # Update a user
            cursor.execute(
                "UPDATE users SET name = %s WHERE email = %s",
                ("Alice Cooper", "alice@example.com")
            )
            conn.commit()
            print("Updated Alice's name")
            
            # Delete a user
            cursor.execute("DELETE FROM users WHERE email = %s", ("bob@example.com",))
            conn.commit()
            print("Deleted Bob")
            
            # Final count
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            print(f"\nFinal user count: {count}")
            
        except Exception as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        
        # Clean up
        postgres.drop_database(database_name)
        print(f"Dropped database: {database_name}")


if __name__ == "__main__":
    psycopg2_example()
