# db.py
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    """
    Handles all database operations for the D&D Manager application,
    including CRUD operations for world building, session notes, and NPCs.
    """
    def __init__(self, db_name='dnd_manager.db'):
        """
        Initializes the Database connection and creates necessary tables.
        """
        try:
            self.conn = sqlite3.connect(db_name)
            self.create_tables()
            logger.info("Connected to the database successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def create_tables(self):
        """
        Creates necessary tables if they do not exist.
        Includes tables for world building, session notes, and NPC management.
        Ensures that 'last_updated' column exists in 'world_building' and 'session_notes' tables.
        """
        try:
            cursor = self.conn.cursor()
            # Table for world-building information
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS world_building (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            ''')
            # Check if 'last_updated' column exists; if not, add it
            cursor.execute("PRAGMA table_info(world_building)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'last_updated' not in columns:
                cursor.execute("ALTER TABLE world_building ADD COLUMN last_updated TIMESTAMP")
                logger.info("Added 'last_updated' column to 'world_building' table.")
                # Set 'last_updated' for existing records
                cursor.execute("UPDATE world_building SET last_updated = CURRENT_TIMESTAMP WHERE last_updated IS NULL")
                logger.info("Set 'last_updated' for existing 'world_building' records.")
            
            # Table for session notes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    notes TEXT NOT NULL
                )
            ''')
            # Check if 'last_updated' column exists; if not, add it
            cursor.execute("PRAGMA table_info(session_notes)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'last_updated' not in columns:
                cursor.execute("ALTER TABLE session_notes ADD COLUMN last_updated TIMESTAMP")
                logger.info("Added 'last_updated' column to 'session_notes' table.")
                # Set 'last_updated' for existing records
                cursor.execute("UPDATE session_notes SET last_updated = CURRENT_TIMESTAMP WHERE last_updated IS NULL")
                logger.info("Set 'last_updated' for existing 'session_notes' records.")

            # Table for NPCs (includes 'faction_affiliation')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS npc (
                    npc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    race TEXT,
                    class TEXT,
                    gender TEXT,
                    age INTEGER,
                    appearance TEXT,
                    background TEXT,
                    languages TEXT,
                    personality_traits TEXT,
                    ideals TEXT,
                    bonds TEXT,
                    flaws TEXT,
                    backstory TEXT,
                    role_in_world TEXT,
                    alignment TEXT,
                    deity TEXT,
                    image_path TEXT,
                    current_location TEXT,
                    faction_affiliation TEXT,
                    current_status TEXT,
                    reputation INTEGER,
                    relationship_to_party TEXT,
                    last_seen TEXT,
                    notes TEXT,
                    possessions TEXT,
                    secrets TEXT,
                    created_on TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            logger.info("Database tables created or verified successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise

    # World Building Methods
    def add_world_building(self, title, content):
        """
        Adds a new world building entry to the database.
        """
        try:
            cursor = self.conn.cursor()
            # Include 'last_updated' in the INSERT statement
            cursor.execute(
                'INSERT INTO world_building (title, content, last_updated) VALUES (?, ?, CURRENT_TIMESTAMP)',
                (title, content)
            )
            self.conn.commit()
            logger.info(f"Added world building entry: {title}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding world building entry: {e}")
            self.conn.rollback()
            raise

    def get_world_building(self):
        """
        Retrieves all world building entries from the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM world_building')
            records = cursor.fetchall()
            logger.info(f"Retrieved {len(records)} world building entries.")
            return records
        except sqlite3.Error as e:
            logger.error(f"Error retrieving world building entries: {e}")
            raise

    def update_world_building(self, record_id, title, content):
        """
        Updates an existing world building entry.
        
        Parameters:
            record_id (int): The ID of the record to update.
            title (str): The new title.
            content (str): The new content.
        
        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE world_building SET title = ?, content = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?',
                (title, content, record_id)
            )
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"Updated world building entry with ID: {record_id}")
                return True
            else:
                logger.warning(f"No world building entry found with ID: {record_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error updating world building entry: {e}")
            self.conn.rollback()
            raise

    # Session Notes Methods
    def add_session_notes(self, date, notes):
        """
        Adds new session notes to the database.
        """
        try:
            cursor = self.conn.cursor()
            # Include 'last_updated' in the INSERT statement
            cursor.execute(
                'INSERT INTO session_notes (date, notes, last_updated) VALUES (?, ?, CURRENT_TIMESTAMP)',
                (date, notes)
            )
            self.conn.commit()
            logger.info(f"Added session notes for date: {date}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding session notes: {e}")
            self.conn.rollback()
            raise

    def get_session_notes(self):
        """
        Retrieves all session notes from the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM session_notes')
            records = cursor.fetchall()
            logger.info(f"Retrieved {len(records)} session notes entries.")
            return records
        except sqlite3.Error as e:
            logger.error(f"Error retrieving session notes: {e}")
            raise

    def update_session_notes(self, record_id, date, notes):
        """
        Updates an existing session notes entry.
        
        Parameters:
            record_id (int): The ID of the record to update.
            date (str): The new date.
            notes (str): The new notes.
        
        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE session_notes SET date = ?, notes = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?',
                (date, notes, record_id)
            )
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"Updated session notes entry with ID: {record_id}")
                return True
            else:
                logger.warning(f"No session notes entry found with ID: {record_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error updating session notes entry: {e}")
            self.conn.rollback()
            raise

    # NPC Management Methods
    def add_npc(self, npc_data):
        """
        Adds a new NPC to the database.
        npc_data should be a dictionary containing NPC attributes.
        """
        try:
            cursor = self.conn.cursor()
            columns = ', '.join(npc_data.keys())
            placeholders = ', '.join(['?'] * len(npc_data))
            values = tuple(npc_data.values())
            query = f'INSERT INTO npc ({columns}) VALUES ({placeholders})'
            cursor.execute(query, values)
            self.conn.commit()
            logger.info(f"Added NPC: {npc_data.get('name', 'Unnamed NPC')}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding NPC: {e}")
            self.conn.rollback()
            raise

    def get_npcs(self):
        """
        Retrieves all NPCs from the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM npc')
            records = cursor.fetchall()
            logger.info(f"Retrieved {len(records)} NPC entries.")
            return records
        except sqlite3.Error as e:
            logger.error(f"Error retrieving NPCs: {e}")
            raise

    def get_npc_by_id(self, npc_id):
        """
        Retrieves a single NPC by its ID.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM npc WHERE npc_id = ?', (npc_id,))
            record = cursor.fetchone()
            if record:
                logger.info(f"Retrieved NPC with ID: {npc_id}")
            else:
                logger.warning(f"No NPC found with ID: {npc_id}")
            return record
        except sqlite3.Error as e:
            logger.error(f"Error retrieving NPC by ID: {e}")
            raise

    def update_npc(self, npc_id, updated_data):
        """
        Updates an existing NPC's data.
        updated_data should be a dictionary containing the fields to update.
        """
        try:
            cursor = self.conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in updated_data.keys()])
            values = tuple(updated_data.values()) + (npc_id,)
            query = f'UPDATE npc SET {set_clause}, last_updated = CURRENT_TIMESTAMP WHERE npc_id = ?'
            cursor.execute(query, values)
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"Updated NPC with ID: {npc_id}")
                return True
            else:
                logger.warning(f"No NPC found to update with ID: {npc_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error updating NPC: {e}")
            self.conn.rollback()
            raise

    def delete_npc(self, npc_id):
        """
        Deletes an NPC from the database by its ID.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM npc WHERE npc_id = ?', (npc_id,))
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"Deleted NPC with ID: {npc_id}")
                return True
            else:
                logger.warning(f"No NPC found to delete with ID: {npc_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error deleting NPC: {e}")
            self.conn.rollback()
            raise

    def get_all_records(self):
        """
        Retrieves all records from world_building and session_notes tables.
        """
        try:
            cursor = self.conn.cursor()
            # Fetch all world-building records with 'last_updated'
            cursor.execute('SELECT id, title, content, last_updated FROM world_building')
            world_records = cursor.fetchall()
            # Fetch all session notes with 'last_updated'
            cursor.execute('SELECT id, date, notes, last_updated FROM session_notes')
            session_records = cursor.fetchall()
            # Fetch all NPC records
            cursor.execute('SELECT * FROM npc')
            npc_records = cursor.fetchall()
            return {
                'world_building': world_records,
                'session_notes': session_records,
                'npc': npc_records
            }
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all records: {e}")
            raise

    def get_record_by_id(self, table, record_id):
        """
        Retrieves a single record by its ID from the specified table.
        
        Parameters:
            table (str): The name of the table ('world_building', 'session_notes', 'npc').
            record_id (int): The ID of the record to retrieve.
        
        Returns:
            tuple: The fetched record, or None if not found.
        """
        try:
            cursor = self.conn.cursor()
            if table == 'world_building':
                cursor.execute('SELECT * FROM world_building WHERE id = ?', (record_id,))
            elif table == 'session_notes':
                cursor.execute('SELECT * FROM session_notes WHERE id = ?', (record_id,))
            elif table == 'npc':
                cursor.execute('SELECT * FROM npc WHERE npc_id = ?', (record_id,))
            else:
                logger.error(f"Unknown table: {table}")
                return None
            record = cursor.fetchone()
            if record:
                logger.info(f"Retrieved record from {table} with ID: {record_id}")
                return record
            else:
                logger.warning(f"No record found in {table} with ID: {record_id}")
                return None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving record by ID: {e}")
            raise

    def close(self):
        """
        Closes the database connection.
        """
        try:
            self.conn.close()
            logger.info("Database connection closed.")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}")
