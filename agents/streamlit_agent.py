import streamlit as st
import mysql.connector
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json
import os

load_dotenv()

client = genai.Client()

# Configuração inicial
st.set_page_config(page_title="Consultas Financeiras", page_icon="🏛️")
st.title("🏛️ LoomBank Consultas")

# Sidebar para credenciais
st.sidebar.header("🔐 Configurações")
genai_api_key = st.sidebar.text_input("Chave da API GenAI", type="password")
mysql_host = st.sidebar.text_input("MySQL Host", value="localhost")
mysql_user = st.sidebar.text_input("Usuário MySQL", value="root")
mysql_password = st.sidebar.text_input("Senha MySQL", type="password")
mysql_db = st.sidebar.text_input("Nome do Banco de Dados", value="loomBank")

# Sessão para manter pergunta sugerida
if "pergunta" not in st.session_state:
    st.session_state.pergunta = ""

# Sugestões de pergunta como no GPT
st.markdown("### 💬 Sugestões de perguntas")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📋 Clientes"):
        st.session_state.pergunta = "Me mostre todos os clientes"
        st.rerun()
with col2:
    if st.button("💸 Pagamentos"):
        st.session_state.pergunta = "Me mostre todos os pagamentos"
        st.rerun()
with col3:
    if st.button("🏠 Endereços"):
        st.session_state.pergunta = "Me mostre todos os endereços"
        st.rerun()
with col4:
    if st.button("📈 Movimentações"):
        st.session_state.pergunta = "Me mostre todas as movimentações"
        st.rerun()

# Campo de pergunta
st.markdown("### ✍️ Pergunta personalizada")
pergunta = st.text_input(
    "Digite sua pergunta em linguagem natural:",
    value=st.session_state.pergunta,
    key="input_pergunta"
)

# Função para obter estrutura das tabelas
def obter_estrutura_tabelas():
    try:
        conn = mysql.connector.connect(
            host = mysql_host,
            user = mysql_user,
            password = mysql_password,
            database = mysql_db,
        )

        cursor = conn.cursor()
        cursor.execute('SHOW TABLES')
        tabelas = cursor.fetchall()

        colunas = {}
        for tabela in tabelas:
            cursor.execute(f"DESCRIBE {tabela[0]};")
            colunas_tabelas = cursor.fetchall()
            colunas[tabela[0]] = [coluna[0] for coluna in colunas_tabelas]

        cursor.close()
        conn.close()
        return colunas
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return {}
    
# Carregar contexto dos prompts
def carregar_prompt():
    try:
        with open("protocols/prompt.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar o contexto do prompt: {e}")
        return {}
    
# Gerar query SQL
def gerar_query_sql(pergunta, colunas, client):
    prompt_data = carregar_prompt()

    system_role = prompt_data.get('model_role', "Você é um assistente de SQL.")
    config = types.GenerateContentConfig(
        system_instruction=system_role, 
        max_output_tokens=300,
        temperature=0
    )

    instrucoes_adicionais = "\n- " + "\n- ".join(prompt_data.get("instrucoes_sql", []))

    contexto = f"""
Sistema: {prompt_data.get('system_name', 'Desconhecido')}
Função do modelo: {system_role}
Perfil do usuário: {prompt_data.get('user_profile', {})}
Restrições: {'; '.join(prompt_data.get('restricoes', []))}

Instruções adicionais para gerar SQL corretamente:
{instrucoes_adicionais}

Base de dados:
{json.dumps(colunas, indent=2, ensure_ascii=False)}

Pergunta do usuário:
{pergunta}

Gere uma consulta SQL correspondente:
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=config,
            contents=[contexto]
        )
        if response.text:
            query = response.text.strip()
            query = query.replace("```sql", "").replace("```", "").strip()
            return query
        else:
            st.error("O modelo não gerou uma resposta válida (conteúdo vazio ou bloqueado).")
            return ""
    
    except Exception as e: 
            st.error(f"Erro ao gerar a query SQL: {e}")
            return ""
    
# Executar query no banco e retornar resultados
def executar_query(query):
    if not query:
        st.warning("⚠️ A consulta SQL está vazia. Verifique sua pergunta ou o contexto.")
        return [], []
    try:
        conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_db
        )
        cursor = conn.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()
        return colunas, resultados
    except Exception as e:
        st.error(f"Erro ao executar a query SQL: {e}")
        return [], []
    
def salvar_historico(pergunta, query, resultado):
    try:
        conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_db
        )
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_interacoes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pergunta TEXT,
                query_gerada TEXT,
                resultado LONGTEXT,
                feedback VARCHAR(10),
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)  

        cursor.execute("""
            INSERT INTO historico_interacoes (pergunta, query_gerada, resultado)
            VALUES (%s, %s, %s)
        """, (pergunta, query, str(resultado)))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao salvar histórico: {e}")

# Salvar feedback
def salvar_feedback(pergunta, feedback):
    try:
        conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_db
        )
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE historico_interacoes
            SET feedback = %s
            WHERE pergunta = %s
            ORDER BY data DESC LIMIT 1;
        """, (feedback, pergunta))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao salvar feedback: {e}")
    
# Execução principal
if pergunta:
    estrutura = obter_estrutura_tabelas()
    if estrutura:
        query = gerar_query_sql(pergunta, estrutura, client)

        # Botão para exibir ou não a query SQL
        mostrar_sql = st.toggle("👁️ Mostrar consulta SQL")
        if mostrar_sql:
            st.code(query, language="sql")

        colunas, resultados = executar_query(query)

        if resultados:
            st.success("✅ Consulta realizada com sucesso!")
            st.dataframe([dict(zip(colunas, row)) for row in resultados])
            salvar_historico(pergunta, query, resultados)
        else:
            st.warning("Nenhum resultado encontrado.")

        feedback = st.radio("Essa resposta foi útil?", ("👍 Sim", "👎 Não"), key="feedback")
        salvar_feedback(pergunta, feedback)