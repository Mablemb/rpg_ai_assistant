# Guia do Projeto: Assistente de Campanha D&D com RAG e XAI

Este guia explica como configurar e usar o Assistente de Campanha D&D com RAG (Retrieval-Augmented Generation) e XAI (Explainable AI).

## Arquivos do Projeto

### Arquivos Principais:
- `setup.py` - Script para configuração inicial do projeto
- `process_data.py` - Processamento de arquivos de texto da campanha
- `create_embeddings.py` - Criação de embeddings e índice FAISS
- `app.py` - Aplicação principal com interface de linha de comando
- `test_rag.py` - Ferramenta para testar apenas o sistema RAG

### Diretórios:
- `data/raw/` - Arquivos de texto da campanha 
- `data/processed/` - Chunks processados
- `models/` - Armazena embeddings e índice FAISS
- `retrieval/` - Componentes do sistema RAG
- `explainer/` - Componentes do sistema XAI
- `output/` - Visualizações e resultados

## Guia Passo a Passo

### 1. Configuração Inicial

Para configurar o projeto pela primeira vez:

```bash
python setup.py
```

Este script vai:
- Criar diretórios necessários
- Gerar arquivos de exemplo da campanha (se não existirem)
- Processar os arquivos em chunks
- Criar embeddings e índice FAISS
- Testar o sistema básico

### 2. Personalização da Campanha

Após a configuração inicial, você pode editar os arquivos da campanha em `data/raw/`:

- `regioes.txt` - Descrição das regiões/locais do seu mundo
- `npcs.txt` - Informações sobre NPCs importantes
- `itens_magicos.txt` - Descrição de itens mágicos
- `monstros.txt` - Informações sobre monstros e criaturas
- `regras_homebrew.txt` - Regras personalizadas

Você também pode adicionar novos arquivos `.txt` com outras categorias de informações.

### 3. Reprocessando Após Alterações

Se você editar os arquivos da campanha, reprocesse-os executando:

```bash
python process_data.py
python create_embeddings.py
```

### 4. Usando o Assistente

Execute o assistente completo com RAG e XAI:

```bash
python app.py
```

Comandos disponíveis durante o uso:
- Digite sua pergunta sobre a campanha
- `noexp [pergunta]` - Desativa as explicações para esta pergunta
- `help` ou `?` - Mostra ajuda
- `exit` ou `quit` - Sai do assistente

### 5. Testando Apenas o RAG

Se quiser testar apenas o componente RAG sem XAI:

```bash
python test_rag.py
```

## Como Funciona

### RAG (Retrieval-Augmented Generation)

1. **Indexação**:
   - Textos da campanha são divididos em chunks
   - Cada chunk é convertido em um embedding vetorial
   - Os embeddings são armazenados em um índice FAISS

2. **Recuperação**:
   - A consulta do usuário é convertida em um embedding
   - O sistema encontra os chunks mais similares semanticamente
   - Esses chunks servem como contexto para a resposta

3. **Geração**:
   - O sistema combina a consulta e o contexto em um prompt
   - Um modelo de linguagem gera uma resposta baseada nesse contexto

### XAI (Explainable AI)

1. **Explicação da Recuperação**:
   - Mostra quais termos da consulta foram importantes
   - Explica por que certos chunks foram recuperados
   - Visualiza a similaridade entre consulta e chunks

2. **Explicação da Geração**:
   - Mapeia trechos da resposta para fontes no contexto
   - Mostra quais fontes foram mais utilizadas
   - Destaca termos importantes nos chunks

## Recursos Avançados e Personalizações

### Melhorando o RAG

- **Modelos Maiores**: Substitua o modelo GPT-2 por modelos maiores como LLama2, Mistral ou GPT-3.5 (requer API key)
- **Chunking Melhorado**: Ajuste os parâmetros de chunking para melhor capturar a semântica dos documentos
- **Embeddings Avançados**: Teste modelos de embedding melhores como `intfloat/e5-large`

### Melhorando o XAI

- **Visualizações Interativas**: Implemente gráficos interativos usando bibliotecas como Plotly
- **Explicações Contrafactuais**: Mostre o que aconteceria se outros chunks fossem utilizados
- **Análise de Confiança**: Adicione métricas de confiança para diferentes partes da resposta

### Expandindo o Sistema

- **Interface Web**: Crie uma interface web usando Flask ou Streamlit
- **Suporte a Imagens**: Adicione capacidade de processar e explicar imagens do seu mundo
- **Persistência de Contexto**: Implemente memória para manter contexto entre perguntas
- **Suporte Multilíngue**: Adicione capacidade de responder em diferentes idiomas

## Conceitos Aprendidos

Através deste projeto, você estará aprendendo:

1. **Conceitos RAG**:
   - Divisão de documentos em chunks semânticos
   - Criação e uso de embeddings para busca semântica
   - Integração de recuperação com geração de texto
   - Uso eficiente de contexto externo para melhorar respostas

2. **Conceitos XAI**:
   - Interpretabilidade de sistemas de IA
   - Explicações sobre decisões de recuperação
   - Rastreabilidade entre resposta e fontes
   - Visualização de processos internos do sistema

3. **Habilidades Técnicas**:
   - Processamento de texto e NLP
   - Uso de embeddings e busca vetorial
   - Integração de componentes em um sistema completo
   - Implementação de sistemas explicáveis

## Próximos Passos

Para avançar além deste projeto inicial:

1. **Melhore o Conteúdo**:
   - Adicione mais informações detalhadas sobre sua campanha
   - Organize melhor os arquivos com seções claras
   - Inclua história, locais, personagens e regras específicas

2. **Aprofunde Tecnicamente**:
   - Experimente diferentes modelos de embedding
   - Teste chunking com sobreposição variável
   - Implemente reranking dos resultados recuperados
   - Explore técnicas mais avançadas de XAI

3. **Expanda para Outros Domínios**:
   - Adapte para outros sistemas de RPG
   - Use para documentação técnica ou manuais
   - Implemente para sua base de conhecimento pessoal
   - Aplique em contextos educacionais ou profissionais

## Solução de Problemas

### Problemas Comuns

1. **Erro de Memória**:
   - Reduza o tamanho do modelo ou o número de chunks
   - Processe os arquivos em lotes menores

2. **Respostas Imprecisas**:
   - Verifique se os arquivos da campanha contêm informações suficientes
   - Ajuste os parâmetros de recuperação (como top_k)
   - Melhore a qualidade dos chunks semânticos

3. **Explicações Confusas**:
   - Simplifique o XAI para mostrar menos detalhes
   - Foque em destacar apenas os termos mais importantes
   - Melhore a visualização dos resultados

### Perguntas Frequentes

**P: Posso usar este sistema sem GPU?**
R: Sim! O sistema foi projetado para rodar em CPU com modelos leves como GPT-2. Para modelos maiores, uma GPU pode ser necessária.

**P: Como expandir para textos maiores?**
R: Divida seus textos em arquivos menores por categoria e ajuste os parâmetros de chunking. Para bases muito grandes, considere usar bancos de dados vetoriais como Chroma ou FAISS com memória mapeada.

**P: É possível integrar com ferramentas de VTT como Roll20 ou Foundry?**
R: Com desenvolvimento adicional, você poderia criar uma API REST para seu assistente e integrá-la via módulos personalizados nessas plataformas.

## Recursos e Referências

- **Bibliotecas Usadas**:
  - LangChain: [https://langchain.readthedocs.io/](https://langchain.readthedocs.io/)
  - FAISS: [https://github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss)
  - Sentence-Transformers: [https://www.sbert.net/](https://www.sbert.net/)
  - HuggingFace Transformers: [https://huggingface.co/docs/transformers/](https://huggingface.co/docs/transformers/)

- **Conceitos RAG**:
  - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2021)
  - "Improving Language Models by Retrieving from Trillions of Tokens" (Borgeaud et al., 2022)

- **Conceitos XAI**:
  - "A Survey of Methods for Explaining Black Box Models" (Guidotti et al., 2018)
  - "Towards Faithful Explanations for Text Classification" (Lei et al., 2016)

---

Esperamos que este projeto seja divertido e educativo, combinando seu interesse em D&D com aprendizado avançado sobre RAG e XAI!

Happy coding & happy gaming! 🧙‍♂️🎲