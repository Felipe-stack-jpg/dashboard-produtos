import streamlit as st
import pandas as pd
import plotly.express as px
import io
from login import valida_senha
from modules.api import carregar_dados

st.set_page_config(page_title='Dashboard Protegida', layout='wide')

if 'Logged_in' not in st.session_state:
    st.session_state.Logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ''

if not st.session_state.Logged_in:
    st.title('Tela de login')

    with st.form('Login_form'):
        st.subheader('insira suas credenciais')
        username = st.text_input('Usuario')
        password = st.text_input('senha', type='password')
        submit = st.form_submit_button('entrar')
    
    if submit:
        if valida_senha(username, password):
            st.session_state.Logged_in = True
            st.session_state.username = username
            st.success(f'Bem vindo, {username}')
            st.rerun()

        else:
            st.error('Usuario ou senha incorretos')
            st.stop()

if st.session_state.Logged_in:
    #header da dashboard
    st.title(' Dashboard de Produtos')

    #conectando na API 
    df = carregar_dados()

    #verificação do status da API
    if df is not None:
        
        #Sidebar com filtro de categoria
        categorias = df['category'].unique()
        categoria_selecionada = st.sidebar.multiselect(
            'Filtrar por Categoria',
            options=categorias,
            default=categorias.tolist()
        )

        #fazendo com que apareça somente a categoria selecionada
        filtro_categoria = df[df['category'].isin(categoria_selecionada)]


        #grafico  de barras (quantidades de produtos por categoria)
        contagem_categoria = filtro_categoria['category'].value_counts().reset_index()
        contagem_categoria.columns = ['categoria', 'quantidade']
        contagem_categoria['categoria'] = contagem_categoria['categoria'].replace({
        'electronics': 'Eletrônicos',
        'jewelery': 'Joias',
        "men's clothing": 'Roupas Masculinas',
        "women's clothing": 'Roupas Femininas'
        })
        #Renomeando categorias
        filtro_categoria = filtro_categoria.rename(columns={
            'id': 'ID',
            'title': 'produto',
            'price': 'preço (USD)',
            'description': 'descrição',
            'category': 'categoria'
        })

        #Filtrar colunas uteis
        filtro_categoria = filtro_categoria[['categoria', 'preço (USD)', 'produto', 'descrição', 'ID']]

         # Criando arquivo Excel na memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtro_categoria.to_excel(writer, index=False, sheet_name='Produtos')
        output.seek(0)

        # Botão para baixar Excel
        st.download_button(
            label= 'Baixar dados filtrados em Excel',
            data=output,
            file_name='produtos_filtrados.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        st.dataframe(filtro_categoria)
        grafico_barras = px.bar(
            contagem_categoria,
            x= 'categoria',
            y= 'quantidade',
            color= 'categoria',
            title=' Quantidade de produtos por categoria'
        )

        grafico_pizza = px.pie(contagem_categoria, names='categoria', values='quantidade')
        

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(grafico_pizza)

        with col2:
            st.plotly_chart(grafico_barras)

        #exibindo informações da api em colunas
        st.subheader('Informações gerais')
        col1,col2,col3,col4,col5 = st.columns(5)
        col1.metric('total de Produtos', len(filtro_categoria))
        col2.metric('Preço Médio (USD)', f"{filtro_categoria['preço (USD)'].mean():.2f}")
        col3.metric('categorias', filtro_categoria['categoria'].nunique())
        col4.metric('Venda Total',f"{filtro_categoria['preço (USD)'].sum():.2f}")
        col5.metric('Produto Mais Vendido',filtro_categoria['produto'.split()[0]].value_counts().idxmax())

        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        import io

        if st.button("Gerar Relatório PDF"):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
            elements = []
            styles = getSampleStyleSheet()

            # Estilo menor para caber na página
            small_style = ParagraphStyle(
                name="Small",
                fontSize=8,
                leading=10
            )

            elements.append(Paragraph("Relatório de Produtos Filtrados", styles["Title"]))
            elements.append(Spacer(1, 12))

            total_produtos = len(filtro_categoria)
            preco_medio = filtro_categoria['preço (USD)'].mean()
            categorias = filtro_categoria['categoria'].nunique()
            venda_total = filtro_categoria['preço (USD)'].sum()

            metricas_texto = f"""
            <b>Total de Produtos:</b> {total_produtos}<br/>
            <b>Preço Médio (USD):</b> {preco_medio:.2f}<br/>
            <b>Categorias:</b> {categorias}<br/>
            <b>Venda Total:</b> {venda_total:.2f}
            """
            elements.append(Paragraph(metricas_texto, styles["Normal"]))
            elements.append(Spacer(1, 12))

            # Cabeçalhos + conteúdo
            data = [filtro_categoria.columns.to_list()]
            for _, row in filtro_categoria.iterrows():
                linha = []
                for item in row:
                    if isinstance(item, str):
                        linha.append(Paragraph(item, small_style))
                    else:
                        linha.append(Paragraph(str(item), small_style))
                data.append(linha)

            # Ajuste de larguras
            table = Table(
                data,
                repeatRows=1,
                colWidths=[80, 50, 120, 450, 50]  # ajuste conforme seu conteúdo
            )

            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.25, colors.black)
            ]))

            elements.append(table)
            doc.build(elements)
            buffer.seek(0)

            st.download_button(
                label="📄 Baixar Relatório PDF (compacto)",
                data=buffer,
                file_name="relatorio_compacto.pdf",
                mime="application/pdf"
            )
    else:
        st.error('Não foi possivel acessar os dados, verifique se você esta conectado a internet!')
