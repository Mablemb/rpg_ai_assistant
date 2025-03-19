"""
Demonstration script for the D&D Campaign Assistant with RAG and XAI.
This script shows how the XAI components help explain the assistant's answers.
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

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "-"*70)
    print(f"  {title}")
    print("-"*70)

def run_demo_query(assistant, retriever, query):
    """Run a demo query and show detailed explanations."""
    print_section(f"CONSULTA: '{query}'")
    
    # Step 1: Retrieve chunks
    print("\n1. RECUPERANDO TRECHOS RELEVANTES...")
    start_time = time.time()
    chunks = retriever.retrieve(query, return_scores=True)
    retrieval_time = time.time() - start_time
    
    print(f"✓ Recuperados {len(chunks)} trechos em {retrieval_time:.2f}s")
    
    # Step 2: Generate answer
    print("\n2. GERANDO RESPOSTA...")
    start_time = time.time()
    response = assistant.answer_query(query, include_context=True, include_sources=True)
    generation_time = time.time() - start_time
    
    print(f"✓ Resposta gerada em {generation_time:.2f}s")
    
    # Step 3: Generate explanations
    print("\n3. GERANDO EXPLICAÇÕES XAI...")
    start_time = time.time()
    explanation = create_simple_explanation(query, chunks, response["answer"])
    explanation_time = time.time() - start_time
    
    print(f"✓ Explicações geradas em {explanation_time:.2f}s")
    
    # Display answer and sources
    print("\n📜 RESPOSTA:")
    print("-"*60)
    print(response["answer"])
    print("-"*60)
    
    if "sources" in response and response["sources"]:
        print("\n📚 FONTES:")
        for source in response["sources"]:
            print(f"- {source}")
    
    # Now show detailed XAI explanations
    print_section("EXPLICAÇÃO XAI DETALHADA")
    
    # 1. Retrieval explanation
    if "retrieval" in explanation:
        retrieval = explanation["retrieval"]
        print("\n🔍 1. EXPLICAÇÃO DA RECUPERAÇÃO:")
        print(f"• {retrieval.get('explanation', 'Sem explicação disponível')}")
        
        if "important_query_terms" in retrieval and retrieval["important_query_terms"]:
            print("\n• Termos importantes na consulta:")
            for term in retrieval["important_query_terms"]:
                print(f"  - {term}")
        
        if "chunk_similarities" in retrieval and retrieval["chunk_similarities"]:
            print("\n• Pontuação de similaridade dos trechos recuperados:")
            for item in retrieval["chunk_similarities"]:
                print(f"  - {item['source']}: {item['similarity']:.4f}")
    
    # 2. Show a highlighted chunk
    if "highlighted_chunks" in explanation and explanation["highlighted_chunks"]:
        print("\n🔎 2. DESTAQUE DE TERMOS:")
        print("• Exemplo de trecho com termos da consulta destacados:")
        chunk = explanation["highlighted_chunks"][0]
        print(f"\nDe '{chunk['source']}':")
        print("-"*60)
        highlight_text = chunk["text"][:300] + "..." if len(chunk["text"]) > 300 else chunk["text"]
        print(highlight_text)
        print("-"*60)
        print("(Os termos destacados aparecem entre ** asteriscos **)")
    
    # 3. Generation explanation
    if "generation" in explanation and "connections" in explanation["generation"]:
        print("\n🧠 3. EXPLICAÇÃO DA GERAÇÃO:")
        print(f"• {explanation['generation'].get('explanation', 'Sem explicação disponível')}")
        
        connections = explanation["generation"]["connections"]
        if connections:
            print("\n• Mapeamento entre resposta e fontes:")
            for i, conn in enumerate(connections[:3]):
                print(f"\n  {i+1}. Resposta: \"{conn['answer_text']}\"")
                print(f"     Baseado em: \"{conn['context_sentence']}\"")
                print(f"     Fonte: {conn['source']}")
                print(f"     Frase correspondente: \"{conn['matched_phrase']}\"")
        
        if "sources_by_usage" in explanation["generation"]:
            print("\n• Uso das fontes na resposta:")
            for source_info in explanation["generation"]["sources_by_usage"]:
                print(f"  - {source_info['source']}: {source_info['count']} trechos")
    
    # 4. Visualizations
    if "visualizations" in explanation:
        print("\n📊 4. VISUALIZAÇÕES:")
        print("• Gráficos gerados:")
        for vis_type, path in explanation["visualizations"].items():
            if path and os.path.exists(path):
                print(f"  - {vis_type}: {path}")
        print("\nAs visualizações foram salvas no diretório 'output'.")
        print("Elas mostram a importância dos termos e a relevância dos trechos recuperados.")
    
    return response, explanation

def main():
    print_header("DEMONSTRAÇÃO DE XAI - ASSISTENTE DE CAMPANHA D&D")
    
    print("\nEste script demonstra como o XAI (Explainable AI) ajuda a entender")
    print("as respostas do assistente de campanha D&D baseado em RAG.")
    
    # Initialize components
    try:
        print("\nInicializando componentes...")
        retriever = CampaignRetriever()
        assistant = CampaignAssistant(retriever=retriever)
        print("Componentes inicializados com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar: {str(e)}")
        print("Certifique-se de que já executou setup.py!")
        sys.exit(1)
    
    # Demo queries - designed to showcase different aspects of the system
    demo_queries = [
        "Quem é a Rainha Elara?",
        "Quais regiões existem neste mundo?",
        "Que itens mágicos poderosos existem na campanha?",
        "Quais são os monstros mais perigosos?",
        "Como funciona a regra de crítico brutal?"
    ]
    
    # Ask user to select a query or enter their own
    print("\nEscolha uma consulta para demonstração ou digite a sua própria:")
    for i, query in enumerate(demo_queries):
        print(f"{i+1}. {query}")
    print("0. Digite sua própria consulta")
    
    choice = input("\nEscolha uma opção (0-5): ")
    
    if choice.isdigit() and 0 <= int(choice) <= len(demo_queries):
        if int(choice) == 0:
            query = input("\nDigite sua pergunta: ")
        else:
            query = demo_queries[int(choice)-1]
        
        # Run the demo
        run_demo_query(assistant, retriever, query)
        
        print_section("CONCLUSÃO")
        print("\nEsta demonstração mostrou como o XAI ajuda a entender:")
        print("1. Por que certos trechos de texto foram recuperados")
        print("2. Quais termos foram importantes na consulta")
        print("3. Como a resposta foi construída a partir do contexto")
        print("4. Como visualizar o processo de recuperação e geração")
        
        print("\nCom XAI, o sistema não é apenas uma 'caixa preta', mas um")
        print("assistente transparente que mostra seu raciocínio!")
    else:
        print("Opção inválida. Por favor, execute o script novamente.")

if __name__ == "__main__":
    main()