import os
import pickle
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline

class CampaignRetriever:
    def __init__(self, models_directory="models", top_k=5):
        """Initialize the campaign knowledge retriever.
        
        Args:
            models_directory: Directory containing the FAISS index and chunks
            top_k: Number of relevant chunks to retrieve
        """
        self.top_k = top_k
        self.models_directory = models_directory
        
        # Check if models exist
        faiss_path = os.path.join(models_directory, "faiss_index.bin")
        chunks_path = os.path.join(models_directory, "chunks.pkl")
        index_to_chunk_path = os.path.join(models_directory, "index_to_chunk.json")
        
        if not (os.path.exists(faiss_path) and 
                os.path.exists(chunks_path) and 
                os.path.exists(index_to_chunk_path)):
            raise FileNotFoundError(
                "Model files not found. Please run process_data.py and create_embeddings.py first."
            )
        
        # Load the embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer("pierreguillou/gpt2-small-portuguese")
        
        # Load FAISS index
        print("Loading FAISS index...")
        self.index = faiss.read_index(faiss_path)
        
        # Load chunks
        print("Loading chunks...")
        with open(chunks_path, 'rb') as f:
            self.chunks = pickle.load(f)
        
        # Load index to chunk mapping
        print("Loading index mapping...")
        with open(index_to_chunk_path, 'r', encoding='utf-8') as f:
            self.index_to_chunk = json.load(f)
        
        print(f"Loaded {len(self.chunks)} chunks and FAISS index from {models_directory}")
    
    def retrieve(self, query, return_scores=False):
        """Retrieve relevant chunks based on the query.
        
        Args:
            query: User query string
            return_scores: Whether to return similarity scores
            
        Returns:
            List of relevant chunks with their text and metadata
        """
        # Generate embedding for the query
        query_embedding = self.embedding_model.encode([query])[0].reshape(1, -1).astype('float32')

        # Print the dimensionality of the query embedding and the FAISS index
        print(f"Query embedding dimensionality: {query_embedding.shape[1]}")
        print(f"FAISS index dimensionality: {self.index.d}")
        
        # Search the FAISS index
        scores, indices = self.index.search(query_embedding, self.top_k)
        
        # Get the actual chunks
        results = []
        for i, idx in enumerate(indices[0]):
            idx_str = str(int(idx))  # Convert numpy int to string
            if idx_str in self.index_to_chunk:
                chunk = self.index_to_chunk[idx_str]
                if return_scores:
                    results.append({
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "score": float(scores[0][i])
                    })
                else:
                    results.append({
                        "text": chunk["text"],
                        "source": chunk["source"]
                    })
        
        return results

class CampaignAssistant:
    def __init__(self, retriever=None, models_directory="models"):
        """Initialize the Campaign Assistant with RAG capabilities.
        
        Args:
            retriever: Instance of CampaignRetriever or None to create a new one
            models_directory: Directory for models
        """
        # Initialize retriever
        if retriever is None:
            try:
                self.retriever = CampaignRetriever(models_directory)
            except FileNotFoundError as e:
                print(f"Error: {str(e)}")
                self.retriever = None
        else:
            self.retriever = retriever
        
        # Initialize text generation model - using a small model that can run locally
        print("Loading text generation model... (this might take a moment)")
        # Inicializar com modelo português, se disponível
        try:
            self.generator = pipeline(
                "text-generation",
                model="pierreguillou/gpt2-small-portuguese",
                max_length=512,
                truncation=True
            )
            print("Modelo PT-BR carregado com sucesso!")
        except:
            # Fallback para o modelo padrão
            print("Modelo PT-BR não disponível, usando modelo padrão.")
            self.generator = pipeline(
                "text-generation",
                model="gpt2",
                max_length=512
            )
    
    def answer_query(self, query, include_context=False, include_sources=True):
        """Answer a campaign related query using RAG.
        
        Args:
            query: User query string
            include_context: Whether to include retrieved context in response
            include_sources: Whether to include source references
            
        Returns:
            Dictionary with answer and optional context/sources
        """
        if self.retriever is None:
            return {
                "answer": "The knowledge base hasn't been properly initialized. Please run setup scripts first.",
                "context": [],
                "sources": []
            }
        
        # Retrieve relevant chunks
        retrieved_chunks = self.retriever.retrieve(query, return_scores=True)
        
        if not retrieved_chunks:
            return {
                "answer": "I don't have enough information to answer that question about your campaign.",
                "context": [],
                "sources": []
            }
        
        # Prepare context for the generator
        context_text = "\n\n".join([chunk["text"] for chunk in retrieved_chunks])
        
        # Generate answer
        if self.generator:
            # Create prompt for the generator
            prompt = f"Answer about a D&D campaign:\nQuestion: {query}\nContext: {context_text}\nAnswer:"
            
            # Generate answer
            try:
                generated_text = self.generator(prompt)[0]["generated_text"]
                
                # Extract just the answer part (after "Answer:")
                answer_parts = generated_text.split("Answer:")
                if len(answer_parts) > 1:
                    answer = answer_parts[1].strip()
                else:
                    answer = "Based on the information in your campaign: " + generated_text
            except Exception as e:
                print(f"Error in text generation: {str(e)}")
                # Fallback to a simple answer based on retrieved chunks
                answer = f"Based on your campaign information: {retrieved_chunks[0]['text'][:200]}..."
        else:
            # Rule-based fallback if no generator is available
            answer = "Based on your campaign information:\n\n"
            for i, chunk in enumerate(retrieved_chunks[:2]):
                answer += f"- {chunk['text'][:150]}...\n\n"
            answer += "(Note: Using retrieved text directly as generation model is unavailable)"
        
        # Prepare response
        response = {"answer": answer}
        
        if include_context:
            response["context"] = [chunk["text"] for chunk in retrieved_chunks]
        
        if include_sources:
            sources = []
            for chunk in retrieved_chunks:
                if chunk["source"] not in sources:
                    sources.append(chunk["source"])
            response["sources"] = sources
        
        return response

# Usage example
if __name__ == "__main__":
    try:
        assistant = CampaignAssistant()
        response = assistant.answer_query("Quais são as regiões importantes da campanha?", include_context=True)
        print(response["answer"])
        print("\nSources:", response["sources"])
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure to run process_data.py and create_embeddings.py first.")