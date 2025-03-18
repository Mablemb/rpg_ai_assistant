"""
Test script for the Campaign Assistant RAG system.
This allows you to interactively query your campaign knowledge base.
"""

from retrieval.rag import CampaignAssistant

def main():
    print("\n" + "="*60)
    print("  D&D CAMPAIGN ASSISTANT - RAG TEST")
    print("="*60)
    print("\nAsk me anything about your campaign!")
    print("Type 'exit' to quit.\n")
    
    try:
        assistant = CampaignAssistant()
        
        while True:
            # Get user input
            query = input("\n🧙 Enter your question: ")
            
            # Check for exit command
            if query.lower() in ('exit', 'quit', 'q'):
                print("\nThank you for using the D&D Campaign Assistant! Farewell, adventurer!")
                break
            
            if not query:
                continue
                
            # Process the query
            response = assistant.answer_query(query, include_context=True, include_sources=True)
            
            # Display the answer
            print("\n📜 ANSWER:")
            print("-" * 60)
            print(response["answer"])
            print("-" * 60)
            
            # Display sources
            if "sources" in response and response["sources"]:
                print("\n📚 SOURCES:")
                for source in response["sources"]:
                    print(f"- {source}")
            
            # Display a sample of the context
            if "context" in response and response["context"]:
                print("\n📄 SAMPLE CONTEXT USED:")
                print(response["context"][0][:200] + "..." 
                      if len(response["context"][0]) > 200 
                      else response["context"][0])
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Make sure you've run setup.py first to prepare the system.")

if __name__ == "__main__":
    main()