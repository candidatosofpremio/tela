import streamlit as st
import os
import pandas as pd
import glob
import openai

# Interface do Streamlit
st.set_page_config(layout="wide")  # Configura o layout para ocupar toda a largura do navegador
st.title("Pergunte ao Orçamento")

# Função para configurar a API da OpenAI
@st.cache_data
def configure_openai_api():
    if "openai_api_configured" not in st.session_state:
        os.environ["OPENAI_API_KEY"] = "sk-proj-Sm8PlmGfRkJouHhMGSUUT3BlbkFJYv5NmBZ90imXwB1hwYfO"
        openai.api_key = "sk-proj-Sm8PlmGfRkJouHhMGSUUT3BlbkFJYv5NmBZ90imXwB1hwYfO"
        st.session_state["openai_api_configured"] = True

configure_openai_api()

# Dicionário de mapeamento de meses
meses = {
    '01': 'Janeiro',
    '02': 'Fevereiro',
    '03': 'Março',
    '04': 'Abril',
    '05': 'Maio',
    '06': 'Junho',
    '07': 'Julho',
    '08': 'Agosto',
    '09': 'Setembro',
    '10': 'Outubro',
    '11': 'Novembro',
    '12': 'Dezembro'
}

# Função para carregar os CSVs
@st.cache_data
def load_csvs(file_pattern):
    all_files = glob.glob(file_pattern)
    dataframes = [pd.read_csv(file, sep=",", encoding='latin1') for file in all_files]
    df = pd.concat(dataframes, ignore_index=True, axis=0)
    df.columns = ['Competência', 'Mês', 'UF', 'Código Siafi', 'Município', 'CPF', 'NIS', 'Favorecido', 'Valor Parcela']
    
    # Transformar os valores dos meses
    df['Mês'] = df['Competência'].astype(str).str[4:6].map(meses)
    
    return df

# Função para criar o comando pandas baseado na pergunta do usuário
def create_pandas_command(question, columns):
    columns_str = ", ".join(columns)
    # Amostra de duas linhas dos dados
    sample_data = """
    Competência, Mês, UF, Código Siafi, Município, CPF, NIS, Favorecido, Valor Parcela
    202101, Janeiro, SP, 1234, São Paulo, 12345678900, 12345678900, João Silva, 100.50
    202102, Fevereiro, RJ, 5678, Rio de Janeiro, 09876543211, 09876543211, Maria Souza, 200.75
    """
    prompt = f"""
    As colunas disponíveis são: {columns_str}.
    
    Aqui está uma amostra dos dados:
    {sample_data}
    
    Transforme a seguinte pergunta em um comando pandas válido que utiliza essas colunas:
    
    Pergunta: {question}
    
    Comando:
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0
    )
    command = response.choices[0].message["content"].strip()
    return command

# Função para executar o comando pandas no DataFrame
def execute_pandas_command(df, command):
    try:
        result = eval(f"{command}")

        return result
    except Exception as e:
        st.write(f"Erro ao executar o comando: {e}")
        return None

# Carregar dados CSV
df = load_csvs("./data/content/dados_extraidos/*.csv")

# Explicação de uso
st.markdown("""
## Como usar a busca
Digite uma pergunta relacionada aos dados disponíveis nas colunas do DataFrame. As colunas disponíveis são:
- Competência
- Mês
- UF
- Código Siafi
- Município
- CPF
- NIS
- Favorecido
- Valor Parcela

### Exemplos de perguntas
1. Qual é o valor total das parcelas por município?
2. Quantas parcelas foram pagas em cada mês?
3. Qual é o valor médio das parcelas por UF?
4. Quais são os municípios com o maior número de favorecidos?
5. Qual é o total de parcelas pagas por competência?
6. Quais CPFs receberam mais de uma parcela?
7. Qual é o total de parcelas pagas por código Siafi?
8. Qual é a distribuição dos valores das parcelas por UF?
9. Quais são os NIS com o maior número de parcelas?
10. Qual é o valor máximo das parcelas pagas por município?
11. Quais são os municípios com o menor valor médio de parcelas?
12. Qual é o total de parcelas pagas por mês e por UF?
13. Quantos favorecidos únicos existem por município?
14. Qual é o valor mínimo das parcelas pagas por competência?
15. Qual é a soma das parcelas pagas por cada favorecido?
16. Quais são os valores das parcelas pagas em um determinado mês?
17. Quais CPFs receberam parcelas em múltiplos meses?
18. Qual é o valor total das parcelas pagas por município e por UF?
19. Quais são os municípios com o maior valor total de parcelas pagas?
20. Qual é a distribuição dos valores das parcelas por mês?

Digite sua pergunta abaixo para obter a resposta.
""")

# Explicação sobre a fonte e limitações dos dados
st.markdown("""
## Fonte dos Dados e Limitações
Os dados utilizados neste experimento foram obtidos do Portal da Transparência do Governo Federal, especificamente da seção Auxílio Brasil. Para este protótipo, a quantidade de dados foi limitada a uma única API e a um único mês (Janeiro de 2023 para o Estado do Ceará) devido às limitações de infraestrutura disponível. Esta abordagem permite a demonstração do protótipo, mas a implementação final poderá incluir um conjunto de dados mais abrangente.
""")

question = st.text_input("Digite sua pergunta:")

if st.button("Obter Resposta"):
    columns = df.columns.tolist()
    command = create_pandas_command(question, columns)
    st.write(f"Comando pandas gerado: {command}")
    result = execute_pandas_command(df, command)
    if result is not None:
        st.write("Resultado da consulta:")
       
        st.dataframe(result, height=800)  # Ajusta a altura conforme necessário
