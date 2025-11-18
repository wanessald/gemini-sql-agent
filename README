### **Agente NL2SQL com Gemini e Streamlit**

Este projeto implementa um Agente de Inteligência Artificial que traduz perguntas em Linguagem Natural (NL) feitas por um usuário em consultas SQL válidas. O agente utiliza a API Google Gemini para a geração do código SQL e o framework Streamlit para a interface web, conectando-se a um banco de dados MySQL para obter e exibir os resultados.

### **Estrutura do Projeto**

A estrutura segue o padrão de projetos Python/Streamlit com módulos dedicados:

```
sqlai-agent/
├── .venv/
├── agents/
│   ├── streamlit_agent.py          # A interface web principal
│   ├── terminal_agent.py           # Agente de teste via console
├── db/                             # Scripts
├── images/                         # Arquivos de imagem
├── protocols/
│   ├── prompt.json                 # Contexto e Regras do Agente
├── .env                            # Variáveis de Ambiente e Credenciais
├── .gitignore
├── .python-version
├── README
└── requirements.txt
```

### **Arquitetura do Agente**

A imagem a seguir ilustra o fluxo de dados e a integração entre os componentes.

<img src="images/arq.png" alt="Arquitetura do Agente" width="50%">

### **Pré-requisitos**

- **Python 3.10+**
- **MySQL Server** rodando (para execução das queries).
- **Chave de API do Gemini** (necessária para a geração do SQL).

### **Ambiente virtual e dependências**

#### Crie e ative o ambiente virtual

```bash
python -m venv .venv

# Windows:
.\.venv\Scripts\Activate
# macOS/Linux
source ./.venv/bin/activate
```

#### Instale as dependências

Instale todos os pacotes necessários definidos no `requirements.txt`:

```bash
pip install streamlit google-genai mysql-connector-python python-dotenv pandas faker
```

### **Variáveis de Ambiente**

Crie o arquivo `.env` para armazenar as credenciais sensíveis e a chave da API.

```bash
# Chave de API do Google Gemini
GEMINI_API_KEY=sua_chave

# Credenciais do MySQL
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DB=seu_banco
```

### **Estrutura do Prompt**

O arquivo `protocols/prompt.json` define as regras de segurança e o comportamento do Agente SQL, garantindo que ele seja um "assistente de dados bancários" seguro.

Regras de Segurança Chave:

- Identidade: model_role define o agente como especialista em SQL para o LoomBank.
- Restrições: Proíbe comandos perigosos como DROP DATABASE ou CREATE DATABASE.
- Resposta: Determina que a saída deve ser apenas a consulta SQL, com explicações apenas em comentários SQL (--).

### **Execução do Projeto**

Para iniciar o Agente SQL, execute o script Streamlit:

```bash
streamlit run agents/streamlit_agent.py
```

### **Aprendizados e Correções Essenciais**

A migração da API OpenAI para a API Gemini foi crucial para entender como o SDK do Google gerencia prompting e a configuração.

1. Mapeamento de Parâmetros da API

   ```bash
   # Ponto de entrada:
   openai.ChatCompletion.create(...) => client.models.generate_content(...)

   # Correção de formato de dict incorreto em contents
   {"role": "system", "content": ...} => config.system_instruction

   # Conflito entre argumentos esperados
   max_tokens=... => config.max_output_tokens=...

   # Extração da query SQL
   response['choices'][0]['message']['content'] => response.text
   ```

2. Correções de Escopo e Sintaxe

   ```bash
   # Tuplas (AttributeError: 'tuple' object...):
   Resolvido removendo a vírgula extra na definição da variável config.

   # Argumentos Ausentes (TypeError: missing 1 required positional argument: 'client'):
   Resolvido passando a instância client para a função gerar_query_sql.

   # Tratamento de Saída (AttributeError: 'NoneType' object...):
   Implementado o if response.text: para evitar falhas quando o modelo não retorna conteúdo (por bloqueio de segurança ou falha de geração).
   ```

3. Correção da Interface Streamlit

   ```bash
   # Problema: O clique nos botões de sugestão não submetia a query.
   # Solução: Adicionar st.rerun() após a atualização de st.session_state.pergunta.

   # Exemplo:
   if st.button("📋 Clientes"):
       st.session_state.pergunta = "Me mostre todos os clientes"
       st.rerun()
   ```

### **Demonstração da Aplicação**

1. **Tela Inicial e Configuração:**

   <img src="images/tela_principal.png" alt="Tela Inicial" width="50%">

2. **Geração e Execução da Query:**

   <img src="images/tela_funcional.gif" alt="Gif exibindo execução da Query" width="50%">
