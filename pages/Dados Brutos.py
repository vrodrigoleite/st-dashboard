import streamlit as st
import requests
import pandas as pd

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url=url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

with st.expander('Colunas'):
    colunas =st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros Dados Brutos')

with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(),dados['Data da Compra'].max())) 

# String para filtrar o df da base de dados
string_query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1]
'''

dados_filtrados = dados.query(string_query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(data=dados_filtrados)

st.markdown(f'{dados_filtrados.shape[0]} linhas, {dados_filtrados.shape[1]} colunas')