"""
Setup script to run all preparation steps for the D&D Campaign Assistant.
This script will:
1. Create sample campaign files if none exist
2. Process the campaign files to create chunks
3. Generate embeddings and create a FAISS index
4. Test the retrieval system with a sample query
"""

import os
import sys
import importlib.util
import time

def load_module(file_path, module_name):
    """Dynamically load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    print("\n" + "="*70)
    print("D&D CAMPAIGN ASSISTANT SETUP".center(70))
    print("="*70 + "\n")
    
    # Check for required directories
    required_dirs = ["data", "data/raw", "data/processed", "models", "retrieval", "explainer", "output"]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"Creating directory: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
    
    # Create retrieval package file
    if not os.path.exists("retrieval/__init__.py"):
        with open("retrieval/__init__.py", "w") as f:
            f.write("# Retrieval package\n")
    
    # Create explainer package file
    if not os.path.exists("explainer/__init__.py"):
        with open("explainer/__init__.py", "w") as f:
            f.write("# Explainer package\n")
    
    # Step 1: Process data
    print("\nSTEP 1: PROCESSING CAMPAIGN FILES")
    print("-"*70)
    
    process_data = load_module("process_data.py", "process_data")
    process_data.create_sample_files("data/raw")
    chunks = process_data.process_campaign_files("data/raw", "data/processed")
    
    if not chunks:
        print("No chunks were created. Please check your campaign files and try again.")
        sys.exit(1)
    
    print(f"Successfully processed {len(chunks)} chunks from campaign files.")
    
    # Step 2: Create embeddings
    print("\nSTEP 2: CREATING EMBEDDINGS AND FAISS INDEX")
    print("-"*70)
    
    create_embeddings = load_module("create_embeddings.py", "create_embeddings")
    embeddings, index = create_embeddings.create_and_save_embeddings(chunks, output_directory="models")
    
    if embeddings is None or index is None:
        print("Failed to create embeddings. Please check the error messages above.")
        sys.exit(1)
    
    print(f"Successfully created embeddings for {len(chunks)} chunks.")
    
    # Create directory for retrieval module if it doesn't exist
    if not os.path.exists("retrieval"):
        os.makedirs("retrieval", exist_ok=True)
    
    # Step 3: Test retrieval
    print("\nSTEP 3: TESTING RETRIEVAL SYSTEM")
    print("-"*70)
    
    # Check if rag.py exists in retrieval directory
    if not os.path.exists("retrieval/rag.py"):
        # If not, show an error message
        print("Error: retrieval/rag.py file not found.")
        print("Please make sure to create this file before running this script.")
        sys.exit(1)
    
    try:
        # Import the retrieval module
        sys.path.insert(0, ".")  # Add current directory to path
        from retrieval.rag import CampaignRetriever, CampaignAssistant
        
        # Create retriever and test it
        print("Testing retrieval system...")
        
        retriever = CampaignRetriever(models_directory="models")
        assistant = CampaignAssistant(retriever=retriever)
        
        # Test queries
        test_queries = [
            "Que regiões existem neste mundo?",
            "Quem é o rei do reino?",
            "Quais itens mágicos existem na campanha?"
        ]
        
        for query in test_queries:
            print(f"\nTesting query: \"{query}\"")
            
            start_time = time.time()
            response = assistant.answer_query(query, include_sources=True)
            elapsed_time = time.time() - start_time
            
            print(f"Response (in {elapsed_time:.2f} seconds):")
            print("-"*40)
            print(response["answer"][:200] + "..." if len(response["answer"]) > 200 else response["answer"])
            print("-"*40)
            
            if "sources" in response and response["sources"]:
                print("Sources:", ", ".join(response["sources"]))
        
        print("\nSETUP COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("You can now use the D&D Campaign Assistant!")
        print("Next steps:")
        print("1. Edit the campaign files in data/raw/ with your own content")
        print("2. Run process_data.py and create_embeddings.py again if you make changes")
        print("3. Implement the XAI components in the explainer directory")
        print("4. Create a main app.py to integrate everything")
        print("="*70)
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        print("Setup completed with warnings. Some components may not work correctly.")

if __name__ == "__main__":
    main()