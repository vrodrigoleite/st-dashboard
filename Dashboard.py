import streamlit as st
import pandas as pd
import requests
import plotly.express as px

def formata_numero(valor, prefixo=''):
    if isinstance(valor, float):
        return f'{prefixo} {round(valor,2)}'
    elif isinstance(valor, int):
        return f'{prefixo} {valor}'

# Configurações do aplicativo
st.set_page_config(layout='wide')

# Adicionando um título ao aplicativo
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

# Acessando os dados da API
url = 'https://labdados.com/produtos'

response = requests.get(url=url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

## Tabelas para construção dos gráficos
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

## Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por estado'
)

fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0, receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita mensal'
)

fig_receita_mensal.update_layout(yaxis_title='Receita')


# Criando as colunas para layout das métricas
coluna1, coluna2 = st.columns(2)

with coluna1:
    # Inserindo métricas
    st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), help='Soma de todos os valores de venda dos produtos')
    st.plotly_chart(fig_mapa_receita, use_container_width=True)
    
with coluna2:
    # Inserindo métricas
    st.metric('Quantidade de vendas', formata_numero(dados.shape[0]), help='Total de registros na tabela de produtos')
    st.plotly_chart(fig_receita_mensal,  use_container_width=True)


# Inserindo o df no Streamlit
st.dataframe(data=dados)
st.dataframe(data=receita_estados)
st.dataframe(data=receita_mensal)