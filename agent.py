# agnoagi
import os
import logging
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from agno.agent import Agent, RunOutput
from agno.team import Team
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb
from agno.tools.duckduckgo import DuckDuckGoTools

# Diretório para o banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "agent.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Database para persistir sessões de usuários
db = SqliteDb(db_file=DB_PATH)

# Modelo compartilhado
model = Gemini(id="gemini-2.5-flash")

# Agente de Programação - ajuda com código e desenvolvimento
programming_agent = Agent(
    id="programming-agent",
    name="Agente de Programação",
    role="Especialista em programação e desenvolvimento de software. Ajuda com código, debugging, boas práticas e linguagens de programação.",
    model=model,
    instructions="Você é um especialista em programação. Ajude com dúvidas de código, explique conceitos de programação, sugira boas práticas e ajude a resolver bugs. Foque em linguagens como Python, Java, JavaScript, C, SQL.",
)

# Agente de Engenharia de Software - processos e metodologias
software_eng_agent = Agent(
    id="software-eng-agent",
    name="Agente de Engenharia de Software",
    role="Especialista em processos de engenharia de software, metodologias ágeis, arquitetura e design de sistemas.",
    model=model,
    instructions="Você é especialista em engenharia de software. Ajude com metodologias (Scrum, Kanban, XP), padrões de projeto, arquitetura de software, UML, requisitos e qualidade de software.",
)

# Agente Acadêmico - ajuda com estudos e carreira
academic_agent = Agent(
    id="academic-agent",
    name="Agente Acadêmico",
    role="Auxilia com dúvidas sobre o curso, matérias, provas, trabalhos e carreira em TI.",
    model=model,
    instructions="Você ajuda estudantes de engenharia de software com dúvidas acadêmicas, dicas de estudo, orientação sobre matérias, preparação para provas e orientação de carreira em TI.",
)

# Agente de Pesquisa - busca informações na web
research_agent = Agent(
    id="research-agent",
    name="Agente de Pesquisa",
    role="Pesquisa informações atualizadas na internet sobre tecnologia, mercado de trabalho e novidades.",
    model=model,
    tools=[DuckDuckGoTools()],
    instructions="""Você é um especialista em pesquisa na web. SEMPRE use a ferramenta de busca para:

1. **Perguntas sobre atualidades**: Notícias de tecnologia, lançamentos, eventos, conferências
2. **Mercado de trabalho**: Vagas, salários, empresas contratando, skills em alta
3. **Documentações e tutoriais**: Buscar documentação oficial, artigos, tutoriais recentes
4. **Ferramentas e bibliotecas**: Novas versões, comparações, alternativas
5. **Tendências**: IA, frameworks, linguagens em crescimento

Dicas de pesquisa:
- Use termos em inglês para resultados mais completos
- Combine múltiplos termos de busca
- Sempre cite as fontes dos resultados
- Priorize resultados recentes (2024-2025)
- Se a primeira busca não retornar bons resultados, tente reformular a query""",
)

# Time de agentes coordenado pelo Cubinho
team = Team(
    name="Cubinho Team",
    members=[programming_agent, software_eng_agent, academic_agent, research_agent],
    model=model,
    instructions="""Você é o Cubinho um Engenheiro de Software, sempre fale de forma clara e objetiva em português brasileiro, como em um chat do Discord.

Sempre que for delegar a tarefa para um agente, apenas repasse a resposta dele não fale que vai mandar a tarefa para um agente! Seja curta, nunca faça mesnagem gigantescas.

## Roteamento de tarefas:
- Dúvidas de código/programação → Agente de Programação
- Metodologias, arquitetura, padrões → Agente de Engenharia de Software  
- Dúvidas do curso, provas, carreira → Agente Acadêmico
- Pesquisas na web, notícias, vagas → Agente de Pesquisa

## IMPORTANTE - Use o Agente de Pesquisa quando:
- Perguntarem sobre NOTÍCIAS, ATUALIDADES ou eventos recentes
- Perguntarem sobre VAGAS de emprego, salários ou mercado de trabalho
- Perguntarem sobre NOVAS VERSÕES de frameworks, linguagens ou ferramentas
- Perguntarem algo que requer informação ATUALIZADA (2024-2025)
- Perguntarem sobre DOCUMENTAÇÃO oficial ou tutoriais específicos
- Perguntarem "como está", "qual o estado atual", "o que há de novo"

Para perguntas gerais ou saudações, responda você mesmo de forma descontraída.""",
    db=db,
    read_chat_history=True,
    enable_agentic_memory=True,
    enable_user_memories=True,
    add_memories_to_context=True,
    markdown=True,
)

def llm_response(prompt: str, user_id: str = "default") -> Optional[str]:
    """
    Envia um prompt para o time de agentes e retorna a resposta.
    Cada usuário tem sua própria sessão persistida.
    
    Args:
        prompt: Texto do prompt a ser enviado
        user_id: ID do usuário do Discord para sessão única
        
    Returns:
        Resposta do modelo em formato de string ou mensagem de erro
    """
    try:
        logger.info(f"Processando prompt para usuário {user_id}: {prompt[:50]}...")
        response = team.run(prompt, session_id=user_id)
        logger.info(f"Resposta gerada com sucesso para usuário {user_id}")
        return response.content
    except ConnectionError as e:
        logger.error(f"Erro de conexão: {e}")
        return "📡 Ops! Tive um problema de conexão. Tente novamente em alguns segundos!"
    except TimeoutError as e:
        logger.error(f"Timeout na requisição: {e}")
        return "⏱️ A requisição demorou demais. Tente uma pergunta mais simples!"
    except Exception as e:
        logger.error(f"Erro inesperado ao processar prompt: {e}", exc_info=True)
        return f"🚨 Algo deu errado! Erro: {type(e).__name__}. Tente novamente ou reporte ao admin."


if __name__ == "__main__":
    print(llm_response("Como funciona o padrão de projeto Singleton?", "test_user"))