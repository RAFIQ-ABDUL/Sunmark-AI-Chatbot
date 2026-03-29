import json
import os
import psycopg2
from pgvector.psycopg2 import register_vector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

def init_db():
    #initializing pg vector
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    
    # 1. Enable the pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # 2. Create the table for school data
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
    register_vector(conn) # Allows psycopg2 to recognize the VECTOR type
    
    embeddings_model = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
    
    # Load the raw data you fetched earlier
    with open("raw_data.json", "r", encoding="utf-8") as f:
        pages = json.load(f)

    # 3. Chunking 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )

    for page in pages:
        chunks = text_splitter.split_text(page["markdown"])
        
        # Batch embed chunks for efficiency
        vectors = embeddings_model.embed_documents(chunks)
        
        for i, chunk in enumerate(chunks):
            cur.execute(
                "INSERT INTO sunmark_docs (content, metadata, embedding) VALUES (%s, %s, %s)",
                (chunk, json.dumps({"source": page["url"]}), vectors[i])
            )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully stored school data in PGVector.")

if __name__ == "__main__":
    process_and_store()