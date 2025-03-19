"""
Simplified XAI module for the D&D Campaign Assistant.
This provides basic explanations for retrievals and answers.
"""

import re
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import os

class SimpleRetrieverExplainer:
    """Explains why certain chunks were retrieved for a query."""
    
    def __init__(self):
        """Initialize the retrieval explainer."""
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def explain_retrieval(self, query, retrieved_chunks):
        """Explain why chunks were retrieved for a query.
        
        Args:
            query: The user query
            retrieved_chunks: List of retrieved text chunks
            
        Returns:
            Dictionary with explanation details
        """
        if not retrieved_chunks:
            return {"explanation": "No chunks were retrieved."}
        
        # Combine query and chunks for vectorization
        all_texts = [query] + [chunk["text"] for chunk in retrieved_chunks]
        
        # Vectorize using TF-IDF
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        except ValueError:
            # Fallback if vectorization fails
            return {"explanation": "Could not generate explanation due to text processing error."}
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Extract important terms from query and chunks
        query_vector = tfidf_matrix[0].toarray()[0]
        important_terms = []
        
        for i, value in enumerate(query_vector):
            if value > 0:
                important_terms.append((feature_names[i], value))
        
        # Sort by importance
        important_terms.sort(key=lambda x: x[1], reverse=True)
        top_terms = important_terms[:5]  # Get top 5 terms
        
        # Get most similar chunks
        chunk_similarities = []
        for i in range(1, len(all_texts)):
            chunk_vector = tfidf_matrix[i].toarray()[0]
            similarity = np.dot(query_vector, chunk_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(chunk_vector) + 1e-8)
            chunk_similarities.append({
                "index": i-1,
                "source": retrieved_chunks[i-1]["source"],
                "similarity": float(similarity)
            })
        
        # Sort by similarity
        chunk_similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return {
            "explanation": "These chunks were retrieved because they contain terms similar to your query.",
            "important_query_terms": [term[0] for term in top_terms],
            "term_weights": top_terms,
            "chunk_similarities": chunk_similarities
        }
    
    def highlight_matched_terms(self, query, chunk_text):
        """Highlight terms from the query that appear in the chunk.
        
        Args:
            query: User query
            chunk_text: Text from a retrieved chunk
            
        Returns:
            Text with highlighted terms
        """
        # Lowercase query and split into words
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        
        # Remove common words (simple stopwords)
        stopwords = {'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das', 
                    'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'e', 'ou', 'que', 'quem', 
                    'quando', 'como', 'onde', 'qual', 'quais', 'the', 'a', 'an', 'and', 'or', 'but', 
                    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
                    'does', 'did', 'to', 'at', 'in', 'on', 'by', 'with', 'about', 'for'}
        
        query_words = query_words - stopwords
        
        # If no meaningful words left, return original text
        if not query_words:
            return chunk_text
        
        # Create a pattern to match any of the query words
        pattern = r'\b(' + '|'.join(query_words) + r')\b'
        
        # Replace occurrences with highlighted version (using asterisks for CLI)
        highlighted_text = re.sub(
            pattern, 
            r'**\1**', 
            chunk_text, 
            flags=re.IGNORECASE
        )
        
        return highlighted_text
    
    def visualize_similarities(self, explanation, output_path=None):
        """Create a bar chart of chunk similarities.
        
        Args:
            explanation: Output from explain_retrieval
            output_path: File path to save the visualization
            
        Returns:
            Path to the saved visualization or None
        """
        if "chunk_similarities" not in explanation or not explanation["chunk_similarities"]:
            return None
        
        plt.figure(figsize=(10, 6))
        
        sources = [item["source"] for item in explanation["chunk_similarities"]]
        similarities = [item["similarity"] for item in explanation["chunk_similarities"]]
        
        plt.bar(range(len(sources)), similarities, color='skyblue')
        plt.xticks(range(len(sources)), sources, rotation=45, ha='right')
        plt.xlabel("Source")
        plt.ylabel("Similarity Score")
        plt.title("Relevance of Retrieved Chunks")
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            plt.close()
            return output_path
        else:
            plt.close()
            return None
    
    def visualize_term_importance(self, explanation, output_path=None):
        """Create a horizontal bar chart of term importance.
        
        Args:
            explanation: Output from explain_retrieval
            output_path: File path to save the visualization
            
        Returns:
            Path to the saved visualization or None
        """
        if "term_weights" not in explanation or not explanation["term_weights"]:
            return None
        
        plt.figure(figsize=(10, 6))
        
        terms = [item[0] for item in explanation["term_weights"]]
        weights = [item[1] for item in explanation["term_weights"]]
        
        y_pos = range(len(terms))
        plt.barh(y_pos, weights, color='lightgreen')
        plt.yticks(y_pos, terms)
        plt.xlabel("Term Weight")
        plt.title("Important Terms in Your Query")
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            plt.close()
            return output_path
        else:
            plt.close()
            return None


class SimpleGenerationExplainer:
    """Explains the generation of answers."""
    
    def __init__(self):
        """Initialize the generation explainer."""
        pass
    
    def explain_answer(self, query, context_chunks, answer):
        """Explain how the answer relates to the context.
        
        Args:
            query: The user query
            context_chunks: Retrieved context chunks
            answer: Generated answer
            
        Returns:
            Dictionary with explanation
        """
        # Combine all context text
        full_context = " ".join([chunk["text"] for chunk in context_chunks])
        
        # Find key phrases from the answer that appear in the context
        # This is a very simple approach - just looking for 3+ word matches
        answer_sentences = answer.split(". ")
        context_sentences = full_context.split(". ")
        
        connections = []
        for ans_sent in answer_sentences:
            ans_words = ans_sent.split()
            if len(ans_words) < 3:  # Skip very short sentences
                continue
                
            # Check for 3-word phrases from answer in context
            for i in range(len(ans_words) - 2):
                phrase = " ".join(ans_words[i:i+3]).lower()
                if phrase in full_context.lower():
                    # Find which context chunk it came from
                    source_chunk = None
                    for chunk in context_chunks:
                        if phrase in chunk["text"].lower():
                            source_chunk = chunk
                            break
                    
                    # Find the full context sentence containing this phrase
                    context_sentence = ""
                    for sent in context_sentences:
                        if phrase in sent.lower():
                            context_sentence = sent
                            break
                    
                    connections.append({
                        "answer_text": ans_sent,
                        "matched_phrase": phrase,
                        "context_sentence": context_sentence,
                        "source": source_chunk["source"] if source_chunk else "Unknown"
                    })
                    break  # Found a match for this answer sentence, move to next one
        
        # Count sources used
        source_counts = {}
        for chunk in context_chunks:
            source = chunk["source"]
            if source in source_counts:
                source_counts[source] += 1
            else:
                source_counts[source] = 1
        
        # Format sources by usage
        sources_by_usage = [{"source": source, "count": count} 
                           for source, count in source_counts.items()]
        sources_by_usage.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "explanation": "The answer was generated by combining information from the retrieved context.",
            "connections": connections[:5],  # Limit to top 5 connections for clarity
            "sources_by_usage": sources_by_usage
        }

# Simple function to create a dummy explanation when real XAI is too complex
def create_simple_explanation(query, retrieved_chunks, answer):
    """Create a simplified explanation of the retrieval and answer.
    
    Args:
        query: User query
        retrieved_chunks: Retrieved chunks with metadata
        answer: Generated answer
        
    Returns:
        Dictionary with explanation text and visualizations
    """
    # Initialize explainers
    retrieval_explainer = SimpleRetrieverExplainer()
    generation_explainer = SimpleGenerationExplainer()
    
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get retrieval explanation
    retrieval_explanation = retrieval_explainer.explain_retrieval(query, retrieved_chunks)
    
    # Get generation explanation
    generation_explanation = generation_explainer.explain_answer(query, retrieved_chunks, answer)
    
    # Create visualizations
    similarity_path = os.path.join(output_dir, "chunk_similarities.png")
    retrieval_explainer.visualize_similarities(retrieval_explanation, similarity_path)
    
    term_path = os.path.join(output_dir, "term_importance.png")
    retrieval_explainer.visualize_term_importance(retrieval_explanation, term_path)
    
    # Highlight terms in chunks
    highlighted_chunks = []
    for chunk in retrieved_chunks:
        highlighted_text = retrieval_explainer.highlight_matched_terms(query, chunk["text"])
        highlighted_chunks.append({
            "text": highlighted_text,
            "source": chunk["source"],
            "score": chunk.get("score", 0)
        })
    
    # Create a combined explanation
    explanation = {
        "retrieval": retrieval_explanation,
        "generation": generation_explanation,
        "highlighted_chunks": highlighted_chunks,
        "visualizations": {
            "similarity": similarity_path if os.path.exists(similarity_path) else None,
            "term_importance": term_path if os.path.exists(term_path) else None
        }
    }
    
    return explanation