"""
Sample patch to app/storage_sqlite.py to add users table to schema.

This shows the specific changes needed to extend init_schema() function.
"""

# ADD THIS TO THE init_schema() FUNCTION IN app/storage_sqlite.py
# After the reservations table creation and before the function ends:

def init_schema(conn: sqlite3.Connection) -> None:
    """
    Initialize database schema with all required tables and indexes.
    
    Args:
        conn: Active database connection
        
    Creates:
        - schema_info table: tracks schema version and migration timestamp
        - rooms table: room inventory with pricing
        - reservations table: guest reservations with status tracking
        - users table: authentication and role-based access control (NEW)
        - idx_reservations_availability: index for fast availability queries
        
    Transaction Handling:
        Caller is responsible for transaction management (BEGIN/COMMIT)
    """
    # ... existing schema_info table creation ...
    
    # ... existing rooms table creation ...
    
    # ... existing reservations table creation ...
    
    # ... existing index creation ...
    
    # ADD THIS SECTION:
    # =========================================================================
    # Users table for authentication and role-based access control
    # =========================================================================
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'staff')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    # =========================================================================
    # END OF ADDITION
    # =========================================================================


# EXAMPLE: Complete updated init_schema() function with users table

"""
def init_schema(conn: sqlite3.Connection) -> None:
    # Schema metadata table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schema_info (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    # Initialize version if not exists
    conn.execute('''
        INSERT OR IGNORE INTO schema_info (key, value)
        VALUES ('version', ?)
    ''', (str(SCHEMA_VERSION),))
    
    # Rooms table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            room_id TEXT PRIMARY KEY,
            room_type TEXT NOT NULL,
            base_price REAL NOT NULL,
            image_path TEXT DEFAULT ''
        )
    ''')
    
    # Reservations table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            room_id TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            guest_phone TEXT NOT NULL,
            guest_email TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            num_guests INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('Confirmed', 'Cancelled', 'Checked-In', 'Checked-Out')),
            total_cost REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
    ''')
    
    # Index for availability queries
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_reservations_availability 
        ON reservations(room_id, start_date, end_date)
    ''')
    
    # Users table (NEW)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'staff')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
"""
