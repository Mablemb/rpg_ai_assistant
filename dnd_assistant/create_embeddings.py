import os
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

def load_chunks(processed_directory):
    """Load processed chunks with metadata."""
    chunks = []
    for filename in os.listdir(processed_directory):
        if filename.endswith('_chunks.txt'):
            source = filename.replace('_chunks.txt', '.txt')
            with open(os.path.join(processed_directory, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                # Split by the separator we used when saving
                chunk_texts = content.split("\n\n---\n\n")
                for chunk_text in chunk_texts:
                    if chunk_text.strip():  # Skip empty chunks
                        chunks.append({"text": chunk_text.strip(), "source": source})
    return chunks

def create_and_save_embeddings(chunks, model_name="all-MiniLM-L6-v2", output_directory="models"):
    """Create embeddings for chunks and save them along with FAISS index."""
    os.makedirs(output_directory, exist_ok=True)
    
    if not chunks:
        print("No chunks to process. Please run process_data.py first.")
        return None, None
    
    # Load model
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Extract texts for embedding
    texts = [chunk["text"] for chunk in chunks]
    
    # Generate embeddings
    print(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Save embeddings and chunks
    with open(os.path.join(output_directory, "chunks.pkl"), 'wb') as f:
        pickle.dump(chunks, f)
    
    # Create FAISS index
    print("Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    # Save FAISS index
    faiss.write_index(index, os.path.join(output_directory, "faiss_index.bin"))
    
    print(f"Saved {len(chunks)} chunks and FAISS index to {output_directory}")
    
    # Save mapping from index to chunk metadata
    index_to_chunk = {i: {"text": chunks[i]["text"], "source": chunks[i]["source"]} 
                      for i in range(len(chunks))}
    
    with open(os.path.join(output_directory, "index_to_chunk.json"), 'w', encoding='utf-8') as f:
        json.dump(index_to_chunk, f, ensure_ascii=False, indent=2)
    
    return embeddings, index

if __name__ == "__main__":
    processed_directory = "data/processed"
    output_directory = "models"
    
    chunks = load_chunks(processed_directory)
    print(f"Loaded {len(chunks)} chunks")
    
    if chunks:
        embeddings, index = create_and_save_embeddings(chunks, output_directory=output_directory)
        print("Embeddings and FAISS index created successfully!")
    else:
        print("No chunks found. Please run process_data.py first to generate chunks.")