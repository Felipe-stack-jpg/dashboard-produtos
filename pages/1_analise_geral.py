import streamlit as st
import pandas as pd
import plotly.express as px
from modules.api import carregar_dados
from modules.utils import to_csv

#header da dashboard
st.set_page_config(page_title= 'Dashboard E-commerce', layout= 'wide')
st.title(' Dashboard de Produtos - Fake Store API')

#conectando na API 
df = carregar_dados()

#verificação do status da API
if df is not None:
    st.subheader('Dados brutos da API:')
    st.dataframe(df)

    #Sidebar com filtro de categoria
    categorias = df['category'].unique()
    categoria_selecionada = st.sidebar.multiselect(
        'Filtrar por Categoria',
        options=categorias,
        default=categorias.tolist()
    )

    #fazendo com que apareça somente a categoria selecionada
    filtro_categoria = df[df['category'].isin(categoria_selecionada)]

    #exibindo informações da api em colunas
    st.subheader('Informações gerais')
    col1,col2,col3 = st.columns(3)
    col1.metric('total de Produtos', len(filtro_categoria))
    col2.metric('Preço Médio (USD)', f'{filtro_categoria['price'].mean():.2f}')
    col3.metric('categorias', filtro_categoria['category'].nunique())

    #grafico  de barras (quantidades de produtos por categoria)
    contagem_categoria = filtro_categoria['category'].value_counts().reset_index()
    contagem_categoria.columns = ['categoria', 'quantidade']
    contagem_categoria['categoria'] = contagem_categoria['categoria'].replace({
    'electronics': 'Eletrônicos',
    'jewelery': 'Joias',
    "men's clothing": 'Roupas Masculinas',
    "women's clothing": 'Roupas Femininas'
    })
    grafico_barras = px.bar(
        contagem_categoria,
        x= 'categoria',
        y= 'quantidade',
        color= 'categoria',
        title=' Quantidade de produtos por categoria'
    )
    st.plotly_chart(grafico_barras,use_container_width= True )


    # Exportar dados filtrados para CSV
    def to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv_data = to_csv(filtro_categoria)
    st.download_button(
        label='Baixar dados filtrados em CSV',
        data= csv_data,
        file_name= 'produtos_filtrados.csv',
        mime='text/csv'
    )

else:
    print('Não foi possivel acessar os dados, verifique se você esta conectado a internet!')
