import json
import os
import psycopg2
from psycopg2.extras import execute_values  # New import for high-speed inserts
from pgvector.psycopg2 import register_vector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from dotenv import load_dotenv

load_dotenv()

def init_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    
    # Enable the pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Create the table for school data
    cur.execute("DROP TABLE IF EXISTS sunmark_docs;")
    cur.execute("""
        CREATE TABLE sunmark_docs (
            id serial PRIMARY KEY,
            content TEXT,
            metadata JSONB,
            embedding VECTOR(384) 
        );
    """)
    conn.commit()
    return conn, cur

def process_and_store():
    # Initialize connection and Embeddings model
    conn, cur = init_db()
    register_vector(conn) 
    
    embeddings_model = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        task="feature-extraction",
        huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY")
    )
    
    file_path = os.path.join(os.path.dirname(__file__), "raw_data.json")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    # 1. Chunking logic
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )

    all_chunks = []
    all_metadata = []

    print("Pre-processing documents...")
    for page in pages:
        chunks = text_splitter.split_text(page["markdown"])
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append(json.dumps({"source": page["url"]}))

    # 2. Global Batch Processing for Speed
    # We send chunks in batches of 32 to minimize network requests to Hugging Face
    batch_size = 32
    total_chunks = len(all_chunks)
    print(f"Total chunks to embed: {total_chunks}")

    for i in range(0, total_chunks, batch_size):
        end_idx = min(i + batch_size, total_chunks)
        batch_texts = all_chunks[i:end_idx]
        batch_metas = all_metadata[i:end_idx]
        
        # Get embeddings from HF API for the whole batch at once
        try:
            batch_vectors = embeddings_model.embed_documents(batch_texts)
            
            # Prepare data for bulk insert
            data_list = [
                (batch_texts[j], batch_metas[j], batch_vectors[j]) 
                for j in range(len(batch_texts))
            ]
            
            # Fast bulk insert using execute_values
            execute_values(
                cur,
                "INSERT INTO sunmark_docs (content, metadata, embedding) VALUES %s",
                data_list
            )
            print(f"Processed {end_idx}/{total_chunks} chunks...")
            
        except Exception as e:
            print(f"Error at batch {i}: {e}")
            continue
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully stored Sunmark data in PGVector.")

if __name__ == "__main__":
    process_and_store()