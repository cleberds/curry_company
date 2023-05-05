import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲'
) #função para juntas as 3 páginas, que deverão ser buscadas dentro da pasta pages, necessariamente.

#image_path = '/Users/clebersc/Documents/Repos/ftc_programacao_python/' comentário feito para remover o caminho absoluto até o arquivo da imagem que está no computador, pq qd estiver na cloud não vai reconhecer o caminho.
#image = Image.open ( image_path + 'logo.png' )
image = Image.open ( 'logo.png' ) #o logo agora ficou no mesmo diretório que está o arquivo Home.py
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Curry Company') #comando cria um título no sidebar, 1 hashtag indica se tratar de subtítulo de 1 nível 1. 
st.sidebar.markdown('## Fastester Delivery in Town') #comando cria um subtítulo no sidebar, 2 hashtags indicam se tratar de subtítulo de nível 2. 
st.sidebar.markdown('''---''') #comando cria linha horizontal que separa o sidebar

st.write( '# Curry Company Growth Dashboard' )

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as métricas de crescimentos dos Entregadores e Restaurantes.
    ### Como utilizar este dashboard?
    - Visão Empresa:
        - Visão Gerencial: métricas gerais de comportamento.
        - Visão Tática: indicadores semanais de crescimento.
        - Visão Geográfica: insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento.
    ### Ask for Help
    - Time de Data Science no Discord
        - @c1eber5c
    ''' )
    