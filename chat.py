# chat.py
import os
import logging
from openai import OpenAI
from anthropic import Anthropic
import faiss
import numpy as np
from db import Database
import tiktoken

logger = logging.getLogger(__name__)

class ChatManager:
    def __init__(self, db, openai_api_key, anthropic_api_key, faiss_index_path='faiss.index', record_ids_path='record_ids.npy'):
        self.db = db
        self.faiss_index_path = faiss_index_path
        self.record_ids_path = record_ids_path
        self.dimension = 1536  # Dimension size for OpenAI's 'text-embedding-3-small'
        self.index = faiss.IndexFlatL2(self.dimension)
        self.record_ids = []
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        if not openai_api_key:
            logger.error("OpenAI API key not found. Please set OPENAI_API_KEY in the environment variables.")
            raise ValueError("OpenAI API key not found.")
        if not anthropic_api_key:
            logger.error("Anthropic API key not found. Please set ANTHROPIC_API_KEY in the environment variables.")
            raise ValueError("Anthropic API key not found.")

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

    def chunk_text(self, text, max_tokens=7500):
        """
        Splits text into chunks of approximately max_tokens.
        """
        tokens = self.tokenizer.encode(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk = self.tokenizer.decode(tokens[i:i + max_tokens])
            chunks.append(chunk)
        return chunks

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
                chunks = self.chunk_text(text)
                for i, chunk in enumerate(chunks):
                    embedding = self.get_embedding(chunk)
                    if embedding:
                        embeddings.append(embedding)
                        self.record_ids.append(('world_building', record[0], i))

            # Index Session Notes Records
            for record in records['session_notes']:
                text = f"Session Notes - {record[1]}: {record[2]}"
                chunks = self.chunk_text(text)
                for i, chunk in enumerate(chunks):
                    embedding = self.get_embedding(chunk)
                    if embedding:
                        embeddings.append(embedding)
                        self.record_ids.append(('session_notes', record[0], i))

            # Index NPC Records
            for npc in npcs:
                npc_text = self.construct_npc_text(npc)
                chunks = self.chunk_text(npc_text)
                for i, chunk in enumerate(chunks):
                    embedding = self.get_embedding(chunk)
                    if embedding:
                        embeddings.append(embedding)
                        self.record_ids.append(('npc', npc[0], i))

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
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            embedding = response.data[0].embedding
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
            elif record_type == 'maps':
                text = f"Map - {record[1]}: Campaign: {record[3]}, World: {record[4]}, Location: {record[5]}, Adventure: {record[6]}, Theme: {record[7]}, Description: {record[8]}"
            else:
                logger.warning(f"Unknown record type: {record_type}")
                return

            chunks = self.chunk_text(text)
            for i, chunk in enumerate(chunks):
                embedding = self.get_embedding(chunk)
                if embedding:
                    embedding_np = np.array([embedding]).astype('float32')
                    self.index.add(embedding_np)
                    self.record_ids.append((record_type, record[0], i))
            
            # Save updated index and record_ids
            faiss.write_index(self.index, self.faiss_index_path)
            np.save(self.record_ids_path, np.array(self.record_ids, dtype=object))
            logger.info(f"Added new {record_type} record to FAISS index.")
        except Exception as e:
            logger.error(f"Error adding record to FAISS index: {e}")

    def search_faiss(self, query, top_k=15):  # Increased from 5 to 15
        """
        Searches the FAISS index for the most relevant records based on the query.
        Returns a list of tuples containing record type, record data, and chunk index.
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
                    record = self.record_ids[idx]
                    if len(record) == 2:
                        record_type, record_id = record
                        chunk_id = 0
                    else:
                        record_type, record_id, chunk_id = record
                    db_record = self.db.get_record_by_id(record_type, record_id)
                    if db_record:
                        relevant_records.append((record_type, db_record, chunk_id))
            logger.info(f"Found {len(relevant_records)} relevant records for the query.")
            return relevant_records
        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}")
            return []

    def refine_prompt(self, user_query, faiss_results):
        """
        Uses Claude-3-Haiku to refine the prompt based on the user query and FAISS results.
        """
        try:
            context = ""
            for record_type, record, chunk_id in faiss_results:
                if record_type == 'world_building':
                    text = f"World Building - Title: {record[1]}\nContent: {record[2]}"
                elif record_type == 'session_notes':
                    text = f"Session Notes - Date: {record[1]}\nNotes: {record[2]}"
                elif record_type == 'npc':
                    text = f"NPC - {record[1]}:\n{self.construct_npc_text(record)}"
                context += f"{text}\n\n"

            if not context:
                context = "No relevant information found in the database."

            system_message = (
                "You are an AI assistant that refines user queries for a D&D game management system. "
                "Given the user's query and context from a FAISS search, produce a concise and focused prompt. "
                "Remove repetitive information and less relevant details. "
                "The refined prompt should capture the essence of the user's query and the most pertinent context."
            )

            user_message = f"User Query: {user_query}\n\nFAISS Context:\n{context}\n\nRefined Prompt:"

            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                temperature=0.7,
                system=system_message,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            refined_prompt = response.content[0].text.strip()
            logger.info("Generated refined prompt using Claude-3-Haiku.")
            return refined_prompt
        except Exception as e:
            logger.error(f"Error refining prompt: {e}")
            return user_query  # Fallback to original query if refinement fails

    def rebuild_faiss_index(self):
        """
        Rebuilds the FAISS index from scratch using all current records.
        """
        try:
            # Clear existing index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.record_ids = []

            # Rebuild index with current data
            records = self.db.get_all_records()
            embeddings = []

            # Process World Building Records
            for record in records['world_building']:
                text = f"World Building - {record['title']}: {record['content']}"
                chunks = self.chunk_text(text)
                for i, chunk in enumerate(chunks):
                    embedding = self.get_embedding(chunk)
                    if embedding:
                        embeddings.append(embedding)
                        self.record_ids.append(('world_building', record['id'], i))

            # Process Session Notes Records
            for record in records['session_notes']:
                text = f"Session Notes - {record['date']}: {record['notes']}"
                chunks = self.chunk_text(text)
                for i, chunk in enumerate(chunks):
                    embedding = self.get_embedding(chunk)
                    if embedding:
                        embeddings.append(embedding)
                        self.record_ids.append(('session_notes', record['id'], i))

            # Process NPC Records
            for npc in records['npc']:
                npc_text = self.construct_npc_text(npc)
                chunks = self.chunk_text(npc_text)
                for i, chunk in enumerate(chunks):
                    embedding = self.get_embedding(chunk)
                    if embedding:
                        embeddings.append(embedding)
                        self.record_ids.append(('npc', npc['npc_id'], i))

            # Process Map Records
            for map_record in records['maps']:
                map_text = f"Map - {map_record['name']}: {map_record['description']}"
                chunks = self.chunk_text(map_text)
                for i, chunk in enumerate(chunks):
                    embedding = self.get_embedding(chunk)
                    if embedding:
                        embeddings.append(embedding)
                        self.record_ids.append(('maps', map_record['id'], i))

            if embeddings:
                embeddings_np = np.array(embeddings).astype('float32')
                self.index.add(embeddings_np)
                faiss.write_index(self.index, self.faiss_index_path)
                np.save(self.record_ids_path, np.array(self.record_ids, dtype=object))
                logger.info("FAISS index rebuilt and saved successfully.")
            else:
                logger.warning("No records found to rebuild FAISS index.")
        except Exception as e:
            logger.error(f"Error rebuilding FAISS index: {e}")
            raise

    def generate_response(self, prompt, chat_history):
        try:
            faiss_results = self.search_faiss(prompt)
            refined_prompt = self.refine_prompt(prompt, faiss_results)

            system_message = (
                "You are a helpful assistant for managing a D&D game. "
                "Use the provided conversation history and refined prompt to answer the user's query thoroughly and accurately."
            )

            # Build the messages list
            messages = []

            # Include the conversation history
            for sender, message in chat_history:
                role = "assistant" if sender == "ChatGPT" else "user"
                messages.append({"role": role, "content": message})

            # Add the refined prompt as the user's latest message
            messages.append({"role": "user", "content": refined_prompt})

            # Log the messages for debugging
            logger.debug(f"Messages sent to LLM:\n{messages}")

            # Call the Anthropic API using messages.create
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=8192,  # Maximum token limit for Claude 3.5 Sonnet
                temperature=0.7,
                system=system_message,
                messages=messages
            )

            logger.info("Generated response from Claude 3.5 Sonnet.")
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, but I encountered an error while trying to generate a response. Please try again later."


            # messages = [
            #     {"role": "system", "content": "You are a helpful assistant for managing a D&D game."},
            #     {"role": "system", "content": f"Here is some relevant information:\n{context}"},
            #     {"role": "user", "content": prompt}
            # ]

            # response = self.client.chat.completions.create(
            #     model="gpt-4",
            #     messages=messages,
            #     max_tokens=500,
            #     n=1,
            #     stop=None,
            #     temperature=0.7,
            # )