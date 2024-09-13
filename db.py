# db.py
import sqlite3
import logging

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
            # Table for session notes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    notes TEXT NOT NULL
                )
            ''')
            # Table for NPCs
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
            # Additional tables for relationships (e.g., languages, factions) can be added here
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
            cursor.execute('INSERT INTO world_building (title, content) VALUES (?, ?)', (title, content))
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

    # Session Notes Methods
    def add_session_notes(self, date, notes):
        """
        Adds new session notes to the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO session_notes (date, notes) VALUES (?, ?)', (date, notes))
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
            # Fetch all world-building records
            cursor.execute('SELECT id, title, content FROM world_building')
            world_records = cursor.fetchall()
            # Fetch all session notes
            cursor.execute('SELECT id, date, notes FROM session_notes')
            session_records = cursor.fetchall()
            return {
                'world_building': world_records,
                'session_notes': session_records
            }
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all records: {e}")
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
