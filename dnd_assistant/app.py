"""
D&D Campaign Assistant with RAG and XAI
Main application that combines retrieval and explanation capabilities.
"""

import os
import sys
import time
# Tenta importar readline (Linux/MacOS) ou pyreadline (Windows)
try:
    import readline  # Para Linux/MacOS
except ImportError:
    try:
        import pyreadline as readline  # Para Windows
    except ImportError:
        # Se nenhum estiver disponível, continue sem readline
        pass

from retrieval.rag import CampaignRetriever, CampaignAssistant
from explainer.xai_simple import create_simple_explanation

class CampaignAssistantApp:
    """Interactive D&D Campaign Assistant with RAG and XAI capabilities."""
    
    def __init__(self, models_directory="models"):
        """Initialize the Campaign Assistant App.
        
        Args:
            models_directory: Directory containing models and data
        """
        # Check if models exist
        if not os.path.exists(os.path.join(models_directory, "faiss_index.bin")):
            print("Models not found. Please run setup.py first.")
            sys.exit(1)
        
        print("Inicializando Assistente de Campanha D&D com RAG e XAI...")
        
        # Initialize components
        try:
            self.retriever = CampaignRetriever(models_directory=models_directory)
            self.assistant = CampaignAssistant(retriever=self.retriever)
        except Exception as e:
            print(f"Erro ao inicializar componentes: {str(e)}")
            sys.exit(1)
        
        # Create output directory for visualizations
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("Assistente de Campanha D&D inicializado e pronto para ajudar!")
    
    def process_query(self, query, explain=True):
        """Process a user query with explanation.
        
        Args:
            query: User query string
            explain: Whether to provide explanations
            
        Returns:
            Response dictionary with answer and explanations
        """
        print("\nProcessando consulta:", query)
        
        # Step 1: Retrieve relevant chunks
        start_time = time.time()
        retrieved_chunks = self.retriever.retrieve(query, return_scores=True)
        retrieval_time = time.time() - start_time
        
        print(f"Recuperados {len(retrieved_chunks)} trechos relevantes em {retrieval_time:.2f}s")
        
        # Step 2: Generate answer
        start_time = time.time()
        response = self.assistant.answer_query(query, include_context=True, include_sources=True)
        generation_time = time.time() - start_time
        
        print(f"Resposta gerada em {generation_time:.2f}s")
        
        # Step 3: Generate explanations if requested
        if explain:
            print("Gerando explicações...")
            
            start_time = time.time()
            explanation = create_simple_explanation(
                query, 
                retrieved_chunks, 
                response["answer"]
            )
            explanation_time = time.time() - start_time
            
            print(f"Explicações geradas em {explanation_time:.2f}s")
            
            # Add explanations to response
            response["explanations"] = explanation
        
        return response
    
    def run_interactive(self):
        """Run the assistant in interactive command-line mode."""
        print("\n" + "="*60)
        print("  Assistente de Campanha D&D com RAG e XAI - Modo Interativo")
        print("="*60)
        print("\nPergunte qualquer coisa sobre sua campanha!")
        print("Digite 'exit' para sair, 'help' para comandos.\n")
        
        while True:
            try:
                # Get user input
                query = input("\n🧙 Digite sua pergunta: ")
                
                # Check for exit command
                if query.lower() in ('exit', 'quit', 'q', 'sair'):
                    print("\nObrigado por usar o Assistente de Campanha D&D! Até a próxima, aventureiro!")
                    break
                
                # Check for help command
                if query.lower() in ('help', '?', 'ajuda'):
                    self.show_help()
                    continue
                
                # Process regular query
                explain = True  # Default to showing explanations
                
                if query.lower().startswith('noexp '):
                    explain = False
                    query = query[6:].strip()
                
                # Process the query
                if not query:
                    continue
                    
                response = self.process_query(query, explain)
                
                # Display the answer
                print("\n📜 RESPOSTA:")
                print("-" * 60)
                print(response["answer"])
                print("-" * 60)
                
                # Display sources
                if "sources" in response and response["sources"]:
                    print("\n📚 FONTES:")
                    for source in response["sources"]:
                        print(f"- {source}")
                
                # Show explanations if enabled
                if explain and "explanations" in response:
                    self.display_explanations(response["explanations"])
                    
                    # Inform about visualizations
                    if "visualizations" in response["explanations"]:
                        print("\n🖼️ VISUALIZAÇÕES:")
                        print(f"As visualizações foram salvas no diretório '{self.output_dir}'.")
                        for vis_type, path in response["explanations"]["visualizations"].items():
                            if path:
                                print(f"- {vis_type}: {path}")
                
            except KeyboardInterrupt:
                print("\n\nSaindo do Assistente de Campanha D&D. Até mais!")
                break
                
            except Exception as e:
                print(f"\nErro: {str(e)}")
                print("Tente outra pergunta ou digite 'exit' para sair.")
    
    def display_explanations(self, explanations):
        """Display the explanations in a user-friendly format.
        
        Args:
            explanations: Dictionary with explanation data
        """
        print("\n🔍 EXPLICAÇÕES:")
        print("-" * 60)
        
        # Retrieval explanation
        if "retrieval" in explanations:
            retrieval = explanations["retrieval"]
            print("\n🔎 Por que esses trechos foram recuperados:")
            print(retrieval.get("explanation", "Nenhuma explicação disponível."))
            
            if "important_query_terms" in retrieval and retrieval["important_query_terms"]:
                print("\nTermos importantes na sua consulta:")
                print(", ".join(retrieval["important_query_terms"]))
        
        # Show a sample of highlighted chunks
        if "highlighted_chunks" in explanations and explanations["highlighted_chunks"]:
            print("\n📑 Exemplo de trecho destacado:")
            chunk = explanations["highlighted_chunks"][0]
            print(f"De {chunk['source']}:")
            # Display first 200 characters of the highlighted text
            highlight_sample = chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"]
            print(highlight_sample)
            print("(** marca os termos correspondentes)")
        
        # Generation explanations
        if "generation" in explanations and "connections" in explanations["generation"]:
            print("\n🧠 Como a resposta foi construída:")
            print(explanations["generation"].get("explanation", ""))
            
            connections = explanations["generation"]["connections"]
            if connections:
                print("\nConexões principais entre fontes e resposta:")
                for i, conn in enumerate(connections[:3]):  # Show top 3
                    print(f"\n{i+1}. Resposta diz: \"{conn['answer_text']}\"")
                    print(f"   Baseado em: \"{conn['context_sentence']}\"")
                    print(f"   De: {conn['source']}")
    
    def show_help(self):
        """Display help information."""
        print("\n📋 COMANDOS DISPONÍVEIS:")
        print("-" * 60)
        print("- [sua pergunta]     Pergunte qualquer coisa sobre sua campanha")
        print("- noexp [pergunta]   Pergunte sem mostrar explicações")
        print("- help / ajuda       Mostra esta informação de ajuda")
        print("- exit / sair        Sai do assistente")
        print("\nExemplos:")
        print("- Quais são as regiões importantes da campanha?")
        print("- Quem é a Rainha Elara?")
        print("- noexp Quais itens mágicos existem?")


if __name__ == "__main__":
    app = CampaignAssistantApp()
    app.run_interactive()