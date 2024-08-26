import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import streamlit_authenticator as stauth

def main():

    # st.set_page_config(layout='centered',page_icon=':bar_chart:')

    def formata_numero(valor, prefixo=''):
        if isinstance(valor, float):
            return f'{prefixo} {round(valor,2)}'
        elif isinstance(valor, int):
            return f'{prefixo} {valor}'

    # Configurações do aplicativo
    # st.set_page_config(layout='wide',page_icon=':bar_chart:')

    # Adicionando um título ao aplicativo
    st.title('RELATÓRIO DE VENDAS')

    # Abas do aplicativo
    tab1, tab2, tab3, tab4 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores', 'dfs'])

    # Acessando os dados da API
    url = 'https://labdados.com/produtos'
    regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

    # Insere barra lateral e seu título
    st.sidebar.title('Filtros')
    regiao = st.sidebar.selectbox('Região', regioes)

    if regiao == 'Brasil':
        regiao = ''

    todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
    if todos_anos:
        ano = ''
    else:
        ano = st.sidebar.slider('Ano', 2020, 2023) 

    query_string = {'regiao': regiao.lower(), 'ano': ano}

    response = requests.get(url=url, params=query_string)
    dados = pd.DataFrame.from_dict(response.json())
    dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

    # Aplicando o filtro de vendedores
    filtro_vendedores = st.sidebar.multiselect(label='Vendedores', options=dados['Vendedor'].unique())
    if filtro_vendedores:
        dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

    # Tabelas
    ## Tabelas de receita

    receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
    receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

    receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'ME'))['Preço'].sum().reset_index()
    receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
    receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

    receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

    ## Tabelas de quantidade de vendas

    ## Tabelas de vendedores

    vendedores = pd.DataFrame(data=dados.groupby('Vendedor')['Preço'].agg(['sum','count']))
    vendedores[['sum']] = vendedores[['sum']].apply(lambda x: round(x, 2))

    # Gráficos
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

    fig_receita_estados = px.bar(receita_estados.head(),
                                x='Local da compra',
                                y='Preço',
                                text_auto=True,
                                title='Top estados (Receita R$)')

    fig_receita_estados.update_layout(yaxis_title='Receita')

    fig_receita_categorias = px.bar(receita_categoria,
                                text_auto=True,
                                title='Receita por categoria')

    fig_receita_categorias.update_layout(yaxis_title='Receita')


    # Criando as colunas para layout das métricas na aba Receita

    with tab1:
        coluna1, coluna2 = st.columns(2)

        with coluna1:
            # Insere as métricas
            st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), help='Soma de todos os valores de venda dos produtos')
            st.plotly_chart(fig_mapa_receita, use_container_width=True)
            st.plotly_chart(fig_receita_estados, use_container_width=True)
            
        with coluna2:
            # Insere as métricas
            st.metric('Quantidade de vendas', formata_numero(dados.shape[0]), help='Total de registros na tabela de produtos')
            st.plotly_chart(fig_receita_mensal,  use_container_width=True)
            st.plotly_chart(fig_receita_categorias, use_container_width=True)

    with tab2:
        coluna1, coluna2 = st.columns(2)

        with coluna1:
            # Insere as métricas
            st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), help='Soma de todos os valores de venda dos produtos')
            
        with coluna2:
            # Insere as métricas
            st.metric('Quantidade de vendas', formata_numero(dados.shape[0]), help='Total de registros na tabela de produtos')

    with tab3:
        qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
        coluna1, coluna2 = st.columns(2)

        with coluna1:
            # Insere as métricas
            st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), help='Soma de todos os valores de venda dos produtos')
            # Constrói a figura
            fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=True).head(qtd_vendedores),
                                            x='sum',
                                            y=vendedores[['sum']].sort_values('sum', ascending=True).head(qtd_vendedores).index,
                                            text_auto=True,
                                            title=f'Top {qtd_vendedores} vendedores (Receita)'
            )
            # Configurando os eixos da figura
            fig_receita_vendedores.update_layout(yaxis_title='Vendedores')
            fig_receita_vendedores.update_layout(xaxis_title='Receita (R$)')
            # Plota a figura
            st.plotly_chart(fig_receita_vendedores)
            
        with coluna2:
            # Inserindo métricas
            st.metric('Quantidade de vendas', formata_numero(dados.shape[0]), help='Total de registros na tabela de produtos')
            fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=True).head(qtd_vendedores),
                                            x='count',
                                            y=vendedores[['count']].sort_values('count', ascending=True).head(qtd_vendedores).index,
                                            text_auto=True,
                                            title=f'Top {qtd_vendedores} vendedores (Total de vendas)'
            )
            fig_vendas_vendedores.update_layout(yaxis_title='Vendedores')
            fig_vendas_vendedores.update_layout(xaxis_title='Total de vendas')
            st.plotly_chart(fig_vendas_vendedores)


    with tab4:
        # Inserindo o df no Streamlit na Aba 2
        st.dataframe(data=dados, use_container_width=True)
        st.dataframe(data=receita_estados)
        st.dataframe(data=receita_mensal)
        st.dataframe(data=receita_categoria)
        st.dataframe(data=vendedores)