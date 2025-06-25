import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Configuração do login
with open('auth_config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)
login_result = authenticator.login("main")
if login_result is not None:
    name, authenticator_status, username = login_result 

    if authenticator_status is False:
        st.error('Usuario ou senha invalidos')
    elif authenticator_status is None:
        st.warning('Por favor, insira suas credenciais')
    elif authenticator_status:
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.success(f'Bem vindo, {name}')


st.set_page_config(page_title='Dashboard E-commerce', layout='wide')

st.image('https://th.bing.com/th/id/OIP.qur2g2wb3Fc6uqu-CDa4bwHaHa?r=0&rs=1&pid=ImgDetMain', width=70)

st.title('Dashboard de Produtos - Fake story')

st.markdown("""
Bem-vindo à dashboard interativa para análise de produtos do nosso e-commerce.

Use o menu lateral para navegar entre as páginas e explorar os dados.

---

### Métricas rápidas:

- Total de produtos: 120
- Vendas mensais: $45.000
- Produtos em promoção: 15
""")