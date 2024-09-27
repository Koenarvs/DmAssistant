import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """
    Handles all database operations for the D&D Manager application,
    including CRUD operations for Maps, World Building, Session Notes, and NPCs.
    """
    def __init__(self, db_path='dnd_manager.db'):
        """
        Initializes the Database connection and creates necessary tables.
        
        Parameters:
            db_path (str): Path to the SQLite database file.
        """
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row  # Enable accessing columns by name
            self.create_tables()
            logger.info("Connected to the database successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def create_tables(self):
        """
        Creates necessary tables if they do not exist.
        Includes tables for Maps, World Building, Session Notes, and NPC Management.
        Ensures that 'last_updated' columns exist where applicable.
        """
        try:
            cursor = self.conn.cursor()

            # ----- Maps Table -----
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    image BLOB,
                    campaign TEXT,
                    world TEXT,
                    location TEXT,
                    adventure TEXT,
                    theme TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("Maps table ensured in database.")

            # ----- World Building Table -----
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS world_building (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("World Building table ensured in database.")

            # ----- Session Notes Table -----
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("Session Notes table ensured in database.")

            # ----- NPC Table -----
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
            logger.info("NPC table ensured in database.")

            self.conn.commit()
            logger.info("All tables created or verified successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            self.conn.rollback()
            raise

    # ----- Maps CRUD Operations -----
    def add_map(self, name, image_data, campaign, world, location, adventure, theme, description):
        """
        Adds a new map to the database.
        
        Parameters:
            name (str): Name of the map.
            image_data (bytes): Binary data of the map image.
            campaign (str): Campaign associated with the map.
            world (str): World name.
            location (str): Specific location.
            adventure (str): Adventure name.
            theme (str): Theme of the map.
            description (str): Description of the map.
        
        Returns:
            int: The ID of the newly added map.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO maps (name, image, campaign, world, location, adventure, theme, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, image_data, campaign, world, location, adventure, theme, description))
            self.conn.commit()
            logger.info(f"Map '{name}' added to database with ID {cursor.lastrowid}.")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding map: {e}")
            self.conn.rollback()
            raise

    def get_maps(self):
        """
        Retrieves all maps from the database.
        
        Returns:
            list of sqlite3.Row: List of maps.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, name, campaign, world, location, adventure, theme, description, created_at, last_updated
                FROM maps
            ''')
            maps = cursor.fetchall()
            logger.info(f"Retrieved {len(maps)} maps from the database.")
            return maps
        except sqlite3.Error as e:
            logger.error(f"Error retrieving maps: {e}")
            raise

    def get_map_by_id(self, map_id):
        """
        Retrieves a single map by its ID.
        
        Parameters:
            map_id (int): The ID of the map to retrieve.
        
        Returns:
            sqlite3.Row or None: The map record if found, else None.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM maps WHERE id = ?
            ''', (map_id,))
            map_record = cursor.fetchone()
            if map_record:
                logger.info(f"Retrieved map with ID: {map_id}")
            else:
                logger.warning(f"No map found with ID: {map_id}")
            return map_record
        except sqlite3.Error as e:
            logger.error(f"Error retrieving map by ID: {e}")
            raise

    def update_map(self, map_id, name, image_data, campaign, world, location, adventure, theme, description):
        """
        Updates an existing map in the database.
        
        Parameters:
            map_id (int): The ID of the map to update.
            name (str): Updated name of the map.
            image_data (bytes): Updated image data.
            campaign (str): Updated campaign.
            world (str): Updated world name.
            location (str): Updated location.
            adventure (str): Updated adventure name.
            theme (str): Updated theme.
            description (str): Updated description.
        
        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE maps
                SET name = ?, image = ?, campaign = ?, world = ?, location = ?, adventure = ?, theme = ?, description = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (name, image_data, campaign, world, location, adventure, theme, description, map_id))
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"Map ID '{map_id}' updated successfully.")
                return True
            else:
                logger.warning(f"No map found with ID: {map_id} to update.")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error updating map: {e}")
            self.conn.rollback()
            return False

    def delete_map(self, map_id):
        """
        Deletes a map from the database by its ID.
        
        Parameters:
            map_id (int): The ID of the map to delete.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM maps WHERE id = ?', (map_id,))
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"Map ID '{map_id}' deleted successfully.")
                return True
            else:
                logger.warning(f"No map found with ID: {map_id} to delete.")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error deleting map: {e}")
            self.conn.rollback()
            return False

    # ----- World Building CRUD Operations -----
    def add_world_building(self, title, content):
        """
        Adds a new world building entry to the database.
        
        Parameters:
            title (str): Title of the world building entry.
            content (str): Content/details of the entry.
        
        Returns:
            int: The ID of the newly added entry.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO world_building (title, content, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (title, content))
            self.conn.commit()
            logger.info(f"Added world building entry: '{title}' with ID {cursor.lastrowid}.")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding world building entry: {e}")
            self.conn.rollback()
            raise

    def get_world_building(self):
        """
        Retrieves all world building entries from the database.
        
        Returns:
            list of sqlite3.Row: List of world building entries.
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

    def get_world_building_by_id(self, record_id):
        """
        Retrieves a single world building entry by its ID.
        
        Parameters:
            record_id (int): The ID of the entry to retrieve.
        
        Returns:
            sqlite3.Row or None: The entry record if found, else None.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM world_building WHERE id = ?', (record_id,))
            record = cursor.fetchone()
            if record:
                logger.info(f"Retrieved world building entry with ID: {record_id}")
            else:
                logger.warning(f"No world building entry found with ID: {record_id}")
            return record
        except sqlite3.Error as e:
            logger.error(f"Error retrieving world building entry by ID: {e}")
            raise

    def update_world_building(self, record_id, title, content):
        """
        Updates an existing world building entry.
        
        Parameters:
            record_id (int): The ID of the entry to update.
            title (str): The new title.
            content (str): The new content.
        
        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE world_building
                SET title = ?, content = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (title, content, record_id))
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"World building entry with ID '{record_id}' updated successfully.")
                return True
            else:
                logger.warning(f"No world building entry found with ID: {record_id} to update.")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error updating world building entry: {e}")
            self.conn.rollback()
            return False

    def delete_world_building(self, record_id):
        """
        Deletes a world building entry from the database by its ID.
        
        Parameters:
            record_id (int): The ID of the entry to delete.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM world_building WHERE id = ?', (record_id,))
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"World building entry with ID '{record_id}' deleted successfully.")
                return True
            else:
                logger.warning(f"No world building entry found with ID: {record_id} to delete.")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error deleting world building entry: {e}")
            self.conn.rollback()
            return False

    # ----- Session Notes CRUD Operations -----
    def add_session_notes(self, date, notes):
        """
        Adds new session notes to the database.
        
        Parameters:
            date (str): Date of the session.
            notes (str): Notes from the session.
        
        Returns:
            int: The ID of the newly added session note.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO session_notes (date, notes, last_updated)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (date, notes))
            self.conn.commit()
            logger.info(f"Added session notes for date: '{date}' with ID {cursor.lastrowid}.")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding session notes: {e}")
            self.conn.rollback()
            raise

    def get_session_notes(self):
        """
        Retrieves all session notes from the database.
        
        Returns:
            list of sqlite3.Row: List of session notes entries.
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

    def get_session_notes_by_id(self, record_id):
        """
        Retrieves a single session note by its ID.
        
        Parameters:
            record_id (int): The ID of the session note to retrieve.
        
        Returns:
            sqlite3.Row or None: The session note record if found, else None.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM session_notes WHERE id = ?', (record_id,))
            record = cursor.fetchone()
            if record:
                logger.info(f"Retrieved session notes entry with ID: {record_id}")
            else:
                logger.warning(f"No session notes entry found with ID: {record_id}")
            return record
        except sqlite3.Error as e:
            logger.error(f"Error retrieving session notes entry by ID: {e}")
            raise

    def update_session_notes(self, record_id, date, notes):
        """
        Updates an existing session notes entry.
        
        Parameters:
            record_id (int): The ID of the session note to update.
            date (str): The new date.
            notes (str): The new notes.
        
        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE session_notes
                SET date = ?, notes = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (date, notes, record_id))
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"Session notes entry with ID '{record_id}' updated successfully.")
                return True
            else:
                logger.warning(f"No session notes entry found with ID: {record_id} to update.")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error updating session notes entry: {e}")
            self.conn.rollback()
            return False

    def delete_session_notes(self, record_id):
        """
        Deletes a session notes entry from the database by its ID.
        
        Parameters:
            record_id (int): The ID of the session note to delete.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM session_notes WHERE id = ?', (record_id,))
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"Session notes entry with ID '{record_id}' deleted successfully.")
                return True
            else:
                logger.warning(f"No session notes entry found with ID: {record_id} to delete.")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error deleting session notes entry: {e}")
            self.conn.rollback()
            return False

    # ----- NPC Management CRUD Operations -----
    def add_npc(self, npc_data):
        """
        Adds a new NPC to the database.
        
        Parameters:
            npc_data (dict): A dictionary containing NPC attributes.
        
        Returns:
            int: The ID of the newly added NPC.
        """
        try:
            cursor = self.conn.cursor()
            columns = ', '.join(npc_data.keys())
            placeholders = ', '.join(['?'] * len(npc_data))
            values = tuple(npc_data.values())
            query = f'INSERT INTO npc ({columns}) VALUES ({placeholders})'
            cursor.execute(query, values)
            self.conn.commit()
            npc_id = cursor.lastrowid
            logger.info(f"Added NPC: '{npc_data.get('name', 'Unnamed NPC')}' with ID {npc_id}.")
            return npc_id
        except sqlite3.Error as e:
            logger.error(f"Error adding NPC: {e}")
            self.conn.rollback()
            raise

    def get_npcs(self):
        """
        Retrieves all NPCs from the database.
        
        Returns:
            list of sqlite3.Row: List of NPC entries.
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
        
        Parameters:
            npc_id (int): The ID of the NPC to retrieve.
        
        Returns:
            sqlite3.Row or None: The NPC record if found, else None.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM npc WHERE npc_id = ?', (npc_id,))
            npc_record = cursor.fetchone()
            if npc_record:
                logger.info(f"Retrieved NPC with ID: {npc_id}")
            else:
                logger.warning(f"No NPC found with ID: {npc_id}")
            return npc_record
        except sqlite3.Error as e:
            logger.error(f"Error retrieving NPC by ID: {e}")
            raise

    def update_npc(self, npc_id, updated_data):
        """
        Updates an existing NPC's data.
        
        Parameters:
            npc_id (int): The ID of the NPC to update.
            updated_data (dict): A dictionary containing the fields to update.
        
        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in updated_data.keys()])
            values = tuple(updated_data.values()) + (npc_id,)
            query = f'''
                UPDATE npc
                SET {set_clause}, last_updated = CURRENT_TIMESTAMP
                WHERE npc_id = ?
            '''
            cursor.execute(query, values)
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"NPC with ID '{npc_id}' updated successfully.")
                return True
            else:
                logger.warning(f"No NPC found with ID: {npc_id} to update.")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error updating NPC: {e}")
            self.conn.rollback()
            return False

    def delete_npc(self, npc_id):
        """
        Deletes an NPC from the database by its ID.
        
        Parameters:
            npc_id (int): The ID of the NPC to delete.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM npc WHERE npc_id = ?', (npc_id,))
            self.conn.commit()
            if cursor.rowcount:
                logger.info(f"NPC with ID '{npc_id}' deleted successfully.")
                return True
            else:
                logger.warning(f"No NPC found with ID: {npc_id} to delete.")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error deleting NPC: {e}")
            self.conn.rollback()
            return False

    # ----- General Record Retrieval Methods -----
    def get_all_records(self):
        """
        Retrieves all records from Maps, World Building, Session Notes, and NPC tables.
        
        Returns:
            dict: A dictionary containing lists of records from each table.
        """
        try:
            cursor = self.conn.cursor()

            # Fetch all maps
            cursor.execute('SELECT * FROM maps')
            maps = cursor.fetchall()

            # Fetch all world-building records
            cursor.execute('SELECT * FROM world_building')
            world_building = cursor.fetchall()

            # Fetch all session notes
            cursor.execute('SELECT * FROM session_notes')
            session_notes = cursor.fetchall()

            # Fetch all NPC records
            cursor.execute('SELECT * FROM npc')
            npcs = cursor.fetchall()

            logger.info("Retrieved all records from Maps, World Building, Session Notes, and NPC tables.")
            return {
                'maps': maps,
                'world_building': world_building,
                'session_notes': session_notes,
                'npc': npcs
            }
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all records: {e}")
            raise

    def get_record_by_id(self, table, record_id):
        """
        Retrieves a single record by its ID from the specified table.
        
        Parameters:
            table (str): The name of the table ('maps', 'world_building', 'session_notes', 'npc').
            record_id (int): The ID of the record to retrieve.
        
        Returns:
            sqlite3.Row or None: The fetched record, or None if not found.
        """
        try:
            cursor = self.conn.cursor()
            if table == 'maps':
                cursor.execute('SELECT * FROM maps WHERE id = ?', (record_id,))
            elif table == 'world_building':
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
                logger.info(f"Retrieved record from '{table}' with ID: {record_id}")
                return record
            else:
                logger.warning(f"No record found in '{table}' with ID: {record_id}")
                return None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving record by ID from '{table}': {e}")
            raise

    # ----- Close Connection -----
    def close(self):
        """
        Closes the database connection.
        """
        try:
            self.conn.close()
            logger.info("Database connection closed.")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}")