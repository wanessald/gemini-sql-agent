import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import mysql.connector

load_dotenv()

host = os.getenv('host')
password = os.getenv('password')
port = os.getenv('port')
user = os.getenv('user')
database = os.getenv('database')
GEMINI_API_KEY = os.getenv('GOOGLE_GENAI_KEY')

conn = mysql.connector.connect(
    host = host,
    password = password,
    port = port,
    user = user,
    database = database,
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

# Construir IA

prompt = f"""
Você é um assistente de SQL que opera para o banco de dados fictício chamado sqlaiBank.
Você deve gerar queries baseadas na seguinte estrutura do banco de dados:
{colunas}
pergunta: {input("faça a sua pergunta: ")}
resposta em SQL:

"""
client = genai.Client()

config = types.GenerateContentConfig(
    system_instruction="Você é um assistente de SQL.",
    max_output_tokens=150,
    temperature=0
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=config,
    contents=[prompt]
)

query_com_tags = response.text

query = query_com_tags.strip()

query_limpa = query.replace("```sql", "").replace("```", "").strip()

conn = mysql.connector.connect(
    host = host,
    password = password,
    port = port,
    user = user,
    database = database,
)

cursor = conn.cursor()

cursor.execute(query_limpa)

resultado = cursor.fetchall()

print(resultado)