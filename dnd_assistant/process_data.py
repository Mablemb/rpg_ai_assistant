import os
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

def read_text_file(file_path):
    """Read text from a text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def clean_text(text):
    """Clean and normalize text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    """Split text into semantically coherent chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks

def process_campaign_files(text_directory, output_directory):
    """Process campaign text files and save chunked text."""
    os.makedirs(output_directory, exist_ok=True)
    
    # Get all text files in the directory
    text_files = [f for f in os.listdir(text_directory) if f.endswith('.txt')]
    
    if not text_files:
        print(f"No text files found in {text_directory}. Please add .txt files first.")
        return []
    
    all_chunks = []
    
    for text_file in text_files:
        file_path = os.path.join(text_directory, text_file)
        print(f"Processing {text_file}...")
        
        # Extract and clean text
        raw_text = read_text_file(file_path)
        cleaned_text = clean_text(raw_text)
        
        # Split into chunks
        chunks = chunk_text(cleaned_text)
        
        # Add source metadata
        chunks_with_metadata = [{"text": chunk, "source": text_file} for chunk in chunks]
        all_chunks.extend(chunks_with_metadata)
        
        # Save chunks to file
        output_file = os.path.join(output_directory, f"{os.path.splitext(text_file)[0]}_chunks.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(chunk + "\n\n---\n\n")
                
    print(f"Processed {len(all_chunks)} chunks from {len(text_files)} files.")
    return all_chunks

def create_sample_files(raw_directory):
    """Create sample campaign files if none exist."""
    os.makedirs(raw_directory, exist_ok=True)
    
    if not os.listdir(raw_directory):
        print("Creating sample campaign files...")
        
        # Sample regions file
        with open(os.path.join(raw_directory, "regioes.txt"), 'w', encoding='utf-8') as f:
            f.write("""# Regiões da Campanha

## Floresta Sombria
A Floresta Sombria fica ao norte do Reino de Valoria. É conhecida por suas árvores altas e densas que bloqueiam a luz do sol. Criaturas feéricas habitam suas profundezas, e dizem que um antigo dragão verde reside em seu coração.

### Locais Importantes
- Torre do Mago Grisalho: Uma torre de pedra abandonada
- Clareira das Fadas: Um círculo de cogumelos onde fadas dançam à noite
- Caverna do Eco: Uma caverna que amplifica sons

## Montanhas Geladas
As Montanhas Geladas formam a fronteira natural entre o Reino de Valoria e as terras bárbaras do norte. Nevascas são comuns durante todo o ano, e apenas os mais resistentes conseguem sobreviver aqui.

### Locais Importantes
- Fortaleza de Gelo: Uma fortaleza habitada por anões das montanhas
- Passagem do Vento Cortante: Um desfiladeiro perigoso e ventoso
- Cavernas de Cristal: Um sistema de cavernas com cristais mágicos

## Cidade de Valoria
Valoria é a capital do reino e um centro de comércio. Suas muralhas de pedra são impressionantes, e suas torres podem ser vistas de quilômetros de distância.

### Locais Importantes
- Castelo Real: Residência do Rei Eldrith IV
- Distrito dos Mercadores: Centro de comércio da cidade
- Templo das Cinco Divindades: O maior templo do reino
""")
        
        # Sample NPCs file
        with open(os.path.join(raw_directory, "npcs.txt"), 'w', encoding='utf-8') as f:
            f.write("""# NPCs Importantes

## Rei Eldrith IV
O atual governante do Reino de Valoria. Um homem idoso com barba grisalha, porém ainda forte e sábio. Conhecido por sua justiça e compaixão, mas implacável com traidores.

### Estatísticas
- Nível: 10
- Classe: Guerreiro/Nobre
- Alinhamento: Leal e Bom

## Arquimaga Lyra
A conselheira mágica do rei e protetora do reino. Uma elfa de mais de 300 anos, com cabelos prateados e olhos de um azul intenso.

### Estatísticas
- Nível: 15
- Classe: Maga (Evocação)
- Alinhamento: Neutro e Bom

## Barakas, o Mercador
Um meio-orc que superou o preconceito para se tornar o mais bem-sucedido mercador de Valoria. Conhecido por sua risada estrondosa e negociações justas.

### Estatísticas
- Nível: 5
- Classe: Ladino/Especialista
- Alinhamento: Neutro
""")
        
        # Sample magic items file
        with open(os.path.join(raw_directory, "itens_magicos.txt"), 'w', encoding='utf-8') as f:
            f.write("""# Itens Mágicos da Campanha

## Espada da Chama Eterna
Uma lâmina lendária forjada nas profundezas do Vulcão Ardente. A lâmina está permanentemente envolta em chamas mágicas que nunca se apagam.

### Propriedades
- +2 de bônus para acerto e dano
- Causa 1d6 de dano de fogo adicional
- 1x por dia pode lançar a magia Bola de Fogo (DC 15)

## Amuleto da Proteção Arcana
Um amuleto de prata com um cristal azul no centro, criado pelos antigos magos de Valoria para proteger contra energias mágicas hostis.

### Propriedades
- +2 de bônus nas jogadas de resistência contra magias
- Resistência a dano de força
- Detecta magia num raio de 30 pés

## Botas do Vento
Botas élficas capazes de aumentar significativamente a velocidade e agilidade de quem as usa.

### Propriedades
- Aumenta a velocidade de movimento em 10 pés
- Vantagem em testes de Acrobacia
- 3x por dia pode usar a ação Disparada como ação bônus
""")
        
        # Sample monsters file
        with open(os.path.join(raw_directory, "monstros.txt"), 'w', encoding='utf-8') as f:
            f.write("""# Monstros da Campanha

## Dragão Verde Ancião Zephyros
Um dragão verde ancião que habita o coração da Floresta Sombria há milênios. É astuto, territorial e adora jogar com suas presas antes de atacar.

### Estatísticas
- CA: 21
- PV: 385 (22d20 + 154)
- Deslocamento: 40 pés, voo 80 pés
- Ataques: Mordida, Garras, Sopro Venenoso (DC 22, 22d6 de dano)

## Golem de Gelo
Construtos mágicos criados pelos anões das Montanhas Geladas para proteger suas fortalezas.

### Estatísticas
- CA: 17
- PV: 157 (15d10 + 75)
- Deslocamento: 30 pés
- Imunidade a dano de frio e veneno
- Fraqueza a dano de fogo

## Assombração do Pântano
Espíritos vingativos que assombram o Pântano Pútrido, restos de guerreiros que morreram em batalhas passadas.

### Estatísticas
- CA: 13
- PV: 67 (9d8 + 27)
- Deslocamento: 0 pés, voo 40 pés
- Resistência a dano não mágico
- Dreno de Vida: 3d6 dano necrótico e cura a mesma quantidade
""")
        
        # Sample homebrew rules file
        with open(os.path.join(raw_directory, "regras_homebrew.txt"), 'w', encoding='utf-8') as f:
            f.write("""# Regras Homebrew da Campanha

## Recuperação de Pontos de Vida
Em nossa campanha, personagens recuperam todos os dados de vida gastos após um descanso longo, e não apenas metade como nas regras padrão.

## Críticos Aprimorados
Em um acerto crítico (rolagem natural de 20), o jogador rola o dano normalmente, depois multiplica o total por 2, em vez de rolar os dados duas vezes.

## Poções como Ação Bônus
Os personagens podem beber uma poção ou administrá-la em um aliado inconsciente usando uma ação bônus, em vez de uma ação completa.

## Resurreição Falível
Quando um personagem é trazido de volta à vida, deve fazer um teste de Constituição (DC 10 + o número de vezes que morreu). Em caso de falha, a ressurreição não funciona e o personagem não pode mais ser ressuscitado.

## Ferimentos Críticos
Quando um personagem é reduzido a 0 pontos de vida e não morre, sofre um ferimento crítico. Role na Tabela de Ferimentos Críticos para determinar o efeito.
""")
        
        print("Sample files created successfully! Edit them with your campaign info or create new .txt files.")

if __name__ == "__main__":
    # Update these paths to your actual directories
    raw_directory = "data/raw"
    output_directory = "data/processed"
    
    # Create sample files if none exist
    create_sample_files(raw_directory)
    
    # Process the campaign files
    chunks = process_campaign_files(raw_directory, output_directory)
    print(f"Processed {len(chunks)} chunks from campaign files.")