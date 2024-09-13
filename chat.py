# chat.py
import os
import logging
import openai
import faiss
import numpy as np
from db import Database

logger = logging.getLogger(__name__)

class ChatManager:
    """
    Manages interactions with OpenAI's ChatGPT and FAISS for semantic search and response generation.
    Handles the indexing of world building, session notes, and NPC data.
    """
    def __init__(self, db, faiss_index_path='faiss.index', record_ids_path='record_ids.npy'):
        """
        Initializes the ChatManager with database connection and FAISS index.
        """
        self.db = db
        self.faiss_index_path = faiss_index_path
        self.record_ids_path = record_ids_path
        self.dimension = 1536  # Dimension size for OpenAI's 'text-embedding-ada-002'
        self.index = faiss.IndexFlatL2(self.dimension)
        self.record_ids = []
        self.load_faiss_index()

    def load_faiss_index(self):
        """
        Loads the FAISS index and record IDs if they exist. Otherwise, builds a new index.
        """
        if os.path.exists(self.faiss_index_path) and os.path.exists(self.record_ids_path):
            try:
                self.index = faiss.read_index(self.faiss_index_path)
                self.record_ids = list(np.load(self.record_ids_path, allow_pickle=True))
                logger.info("FAISS index loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")
                logger.info("Attempting to rebuild FAISS index...")
                self.build_faiss_index()
        else:
            logger.info("FAISS index not found. Building a new index...")
            self.build_faiss_index()

    def build_faiss_index(self):
        """
        Builds the FAISS index from existing world building, session notes, and NPC records.
        """
        try:
            records = self.db.get_all_records()
            npcs = self.db.get_npcs()
            embeddings = []
            self.record_ids = []

            # Index World Building Records
            for record in records['world_building']:
                text = f"World Building - {record[1]}: {record[2]}"
                embedding = self.get_embedding(text)
                if embedding:
                    embeddings.append(embedding)
                    self.record_ids.append(('world_building', record[0]))

            # Index Session Notes Records
            for record in records['session_notes']:
                text = f"Session Notes - {record[1]}: {record[2]}"
                embedding = self.get_embedding(text)
                if embedding:
                    embeddings.append(embedding)
                    self.record_ids.append(('session_notes', record[0]))

            # Index NPC Records
            for npc in npcs:
                # Concatenate relevant NPC fields for embedding
                npc_text = self.construct_npc_text(npc)
                embedding = self.get_embedding(npc_text)
                if embedding:
                    embeddings.append(embedding)
                    self.record_ids.append(('npc', npc[0]))  # Assuming npc_id is the first field

            if embeddings:
                embeddings_np = np.array(embeddings).astype('float32')
                self.index = faiss.IndexFlatL2(self.dimension)
                self.index.add(embeddings_np)
                faiss.write_index(self.index, self.faiss_index_path)
                np.save(self.record_ids_path, np.array(self.record_ids, dtype=object))
                logger.info("FAISS index built and saved successfully.")
            else:
                logger.warning("No records found to build FAISS index.")
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}")
            raise

    def construct_npc_text(self, npc_record):
        """
        Constructs a text representation of an NPC for embedding.
        """
        try:
            npc = {
                'npc_id': npc_record[0],
                'name': npc_record[1],
                'race': npc_record[2],
                'class': npc_record[3],
                'gender': npc_record[4],
                'age': npc_record[5],
                'appearance': npc_record[6],
                'background': npc_record[7],
                'languages': npc_record[8],
                'personality_traits': npc_record[9],
                'ideals': npc_record[10],
                'bonds': npc_record[11],
                'flaws': npc_record[12],
                'backstory': npc_record[13],
                'role_in_world': npc_record[14],
                'alignment': npc_record[15],
                'deity': npc_record[16],
                'current_location': npc_record[17],
                'faction_affiliation': npc_record[18],
                'current_status': npc_record[19],
                'reputation': npc_record[20],
                'relationship_to_party': npc_record[21],
                'last_seen': npc_record[22],
                'notes': npc_record[23],
                'possessions': npc_record[24],
                'secrets': npc_record[25]
            }
            npc_text = "\n".join([f"{key.capitalize()}: {value}" for key, value in npc.items() if value])
            return f"NPC - {npc['name']}: {npc_text}"
        except Exception as e:
            logger.error(f"Error constructing NPC text: {e}")
            return ""

    def get_embedding(self, text):
        """
        Retrieves the embedding for a given text using OpenAI's Embedding API.
        """
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            embedding = response['data'][0]['embedding']
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def add_record_to_index(self, record_type, record):
        """
        Adds a single record's embedding to the FAISS index incrementally.
        """
        try:
            if record_type == 'world_building':
                text = f"World Building - {record[1]}: {record[2]}"
            elif record_type == 'session_notes':
                text = f"Session Notes - {record[1]}: {record[2]}"
            elif record_type == 'npc':
                text = self.construct_npc_text(record)
            else:
                logger.warning(f"Unknown record type: {record_type}")
                return

            embedding = self.get_embedding(text)
            if embedding:
                embedding_np = np.array([embedding]).astype('float32')
                self.index.add(embedding_np)
                self.record_ids.append((record_type, record[0]))
                # Save updated index and record_ids
                faiss.write_index(self.index, self.faiss_index_path)
                np.save(self.record_ids_path, np.array(self.record_ids, dtype=object))
                logger.info(f"Added new {record_type} record to FAISS index.")
        except Exception as e:
            logger.error(f"Error adding record to FAISS index: {e}")

    def search_faiss(self, query, top_k=5):
        """
        Searches the FAISS index for the most relevant records based on the query.
        Returns a list of tuples containing record type and record data.
        """
        try:
            embedding = self.get_embedding(query)
            if embedding is None:
                logger.warning("No embedding found for the query.")
                return []

            embedding_np = np.array([embedding]).astype('float32')
            distances, indices = self.index.search(embedding_np, top_k)

            relevant_records = []
            for idx in indices[0]:
                if idx < len(self.record_ids):
                    record_type, record_id = self.record_ids[idx]
                    record = self.db.get_record_by_id(record_type, record_id)
                    if record:
                        relevant_records.append((record_type, record))
            logger.info(f"Found {len(relevant_records)} relevant records for the query.")
            return relevant_records
        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}")
            return []

    def generate_response(self, prompt):
        """
        Generates a response from ChatGPT based on the user's prompt and relevant context retrieved via FAISS.
        """
        try:
            relevant_records = self.search_faiss(prompt)
            context = ""
            for record_type, record in relevant_records:
                if record_type == 'world_building':
                    context += f"World Building - Title: {record[1]}\nContent: {record[2]}\n\n"
                elif record_type == 'session_notes':
                    context += f"Session Notes - Date: {record[1]}\nNotes: {record[2]}\n\n"
                elif record_type == 'npc':
                    context += f"NPC - {record[1]}:\n"
                    npc_text = self.construct_npc_text(record)
                    context += f"{npc_text}\n\n"

            if not context:
                context = "No relevant information found in the database."

            messages = [
                {"role": "system", "content": "You are a helpful assistant for managing a D&D game."},
                {"role": "system", "content": f"Here is some relevant information:\n{context}"},
                {"role": "user", "content": prompt}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                n=1,
                stop=None,
                temperature=0.7,
            )
            logger.info("Generated response from ChatGPT.")
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, but I encountered an error while trying to generate a response. Please try again later."
