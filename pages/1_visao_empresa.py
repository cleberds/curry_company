# importar bibliotecas
import pandas as pd #se o terminal não reconhecer o pandas, o pacote deve ser instalado no terminal (pip install pandas) 
import re
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image #biblioteca de edição de imagens

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )#expandir o gráfico
# ----------------------------------------
# Funções
# ----------------------------------------

def clean_code( df1 ): #clean_code recebe df1
    ''' 
        ESta função tem a responsabilidade de limpar o dataframe
        tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
        
        Input: Dataframe
        Output: Dataframe
    '''
    # excluir as linhas que contenham dados 'NaN'
    limpa_age = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[limpa_age, :]

    limpa_city = df1['City'] != 'NaN'
    df1 = df1.loc[limpa_city,:]

    limpa_rating = df1['Delivery_person_Ratings'] != 'NaN '
    df1 = df1.loc[limpa_rating,:]

    limpa_festival = df1['Festival'] != 'NaN'
    df1 = df1.loc[limpa_festival, :]

    limpa_weather = df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[limpa_weather, :]

    limpa_multdelivery = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[limpa_multdelivery, :]

    # converter os formatos de texto/categoria/string para os formatos adequados
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # remover espaco da string
    colunas = ['ID', 'Delivery_person_ID', 'Type_of_order', 'Type_of_vehicle', 'City', 'Road_traffic_density', 'Festival']
    for i in colunas:
      df1.loc[:,i] = df1.loc[:,i].str.strip()

    # limpar a coluna 'Time_taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1 
#clean_code retorna df1


def order_metric ( df1 ):
    coluna1 = ['ID','Order_Date'] #colunas
    filtro1 = df1.loc[:,coluna1].groupby('Order_Date').count().reset_index() #seleção de linhas
    fig = px.bar( filtro1, x='Order_Date', y='ID' )
    return fig
#função recebe um dataframe, executa o dataframe, gera uma figura e passa a figura para o fig


def traffic_order_share( df1 ):
    filtro3 = df1[['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index() #selecionando as colunas para agrupar e contar os valores por densidade de tráfego
    filtro3['%_Entregas'] = filtro3['ID'] / filtro3['ID'].sum() #criando a nova coluna de percentuais
    fig = px.pie(filtro3, values = '%_Entregas', names = 'Road_traffic_density') #desenhando o gráfico de pizza
    return fig

def traffic_order_city ( df1 ):
    coluna4 = ['ID','City','Road_traffic_density'] #colunas
    filtro4 = df1.loc[:,coluna4].groupby(['City','Road_traffic_density']).count().reset_index() #selecionando as linhas para agrupar por densidade de tráfego e cidade e contar as entregas
    fig = px.scatter(filtro4, y = 'Road_traffic_density', x = 'City', size = 'ID', color = 'City') #desenhando o gráfico de bolhas
    return fig

def order_by_week (df1):
    df1['Week_of_Year'] = df1['Order_Date'].dt.strftime('%U')
    filtro2 = df1[['ID','Week_of_Year']].groupby('Week_of_Year').count().reset_index()
    fig = px.line(filtro2, x = 'Week_of_Year', y = 'ID')
    return fig

def order_share_by_week (df1):
    filtro5_id = df1[['ID','Week_of_Year']].groupby('Week_of_Year').count().reset_index() #(tab1) qtd de pedidos por semana
    filtro5_person = df1[['Delivery_person_ID','Week_of_Year']].groupby('Week_of_Year').nunique().reset_index() #(tab2) qtd de entregadores únicos por semana
    filtro5 = pd.merge(filtro5_id, filtro5_person, how = 'inner', on = 'Week_of_Year') #(tab3) união das duas tabelas (tab1 + tab2)
    filtro5['Order_by_deliver'] = filtro5['ID'] / filtro5['Delivery_person_ID'] #cria coluna com cálculo de qtd_id / qtd_person na tab3
    fig = px.line(filtro5, x = 'Week_of_Year', y = 'Order_by_deliver') #gráfico da tab3
    return fig

def country_maps ( df1 ):
    coluna6 = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    filtro6 = df1[coluna6].groupby(['City','Road_traffic_density']).median().reset_index()

    map = folium.Map() #comando que desenha o mapa

    for index, location_info in filtro6.iterrows(): #comando para inserir as marcas das coordenadas no mapa
        folium.Marker([location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
                    popup = location_info[['City','Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024,height=600) #comando que permite executar o folium.Map() no streamlit.
#a própria função vai desenhar o mapa, não precisa retornar nada.

# ------------------------------ Início da Estrutura Lógica do Código ------------------------------
# ----------------------------------------
# Import dataset
# ----------------------------------------
df = pd.read_csv('dataset/train.csv') #no google colab usa-se o 'cl.files.upload()' para subir o arquivo da máquina para as nuvens. Aqui basta indicar o caminho onde está o arquivo.

# ----------------------------------------
# Limpando os dados
# ----------------------------------------
df1 = clean_code( df ) 
#comando acima chama a função clean_code(df) e retorna o valor do df1
#NÃO ENTENDI PQ O COMANDO CHAMA A FUNÇÃO PARA PASSAR O DF E NÃO O DF1.
#NÃO ENTENDI PQ ESTE COMANDO SUBSTITUI O DF1 = DF.COPY()

# =======================================
# Barra lateral
# ======================================= 
#a construção do layout é baseado no arquivo 'planejamento_dashboard.drawio', e feito no caminho 'docs => API reference'
#os comandos são construídos no Python File (visao_empresa.py), o terminal compila os comandos e executa em um navegador que será aberto automaticamente.
#a cada etapa de estruturação no terminaL deve ser rodado o comando 'streamlit run visao_empresa.py', que executará as alterações do arquivo fonte diretamente no navegador, deixando o terminal ocupado de modo ininterrupto. Para parar o run e possibilitar executar mais comandos, acionar o Ctrl+C no terminal. 
#no navegador gerado pelo streamlit run, clicar no 'always rerun' para que seja reconhecida e apresentada automaticamente na tela qualquer alteração nos construção dos comandos do arquivo Python File. 

st.header('Marketplace - Visão Cliente') #comando cria um título na região macro ('docs => API reference => Text elements => st.header')

#image_path = 'logo.png'
#image = Image.open(image_path)

image = Image.open( 'logo.png' )
st.sidebar.image( image, width=200 ) #o comando st.image vai pedir uma variável e um tamanho da imagem. Para buscar uma imagem do computador para dentro do streamlit é preciso usar uma função Image.open, que pedirá o caminho onde está armazenada a imagem.

st.sidebar.markdown('# Curry Company') #comando cria um título no sidebar, 1 hashtag indica se tratar de subtítulo de 1 nível 1. 
st.sidebar.markdown('## Fastester Delivery in Town') #comando cria um subtítulo no sidebar, 2 hashtags indicam se tratar de subtítulo de nível 2. 
st.sidebar.markdown('''---''') #comando cria linha horizontal que separa o sidebar
st.sidebar.markdown('## Selecione uma data limite') #comando cria o título de um filtro
date_slider = st.sidebar.slider(
                                'Até qual valor?', #texto que aparece acima do controle deslizante na barra lateral;
                                value=pd.datetime( 2022, 4, 13 ), #data default
                                min_value=pd.datetime( 2022, 2, 11 ), #menor data do df1 (st.dataframe( df1))
                                max_value=pd.datetime( 2022, 4, 6 ), #maior data do df1 (st.dataframe( df1))
                                format='DD-MM-YYYY' ) #formato que a data vai aparecer
#o st.sidebar.slider é filtro cria controle deslizante que permite selecionar um número entre valor min e máx:
#o date_slider recebe o filtro, que tem um texto e um intervalo de valores que ele pode assumir ('API reference => Input widgets => st.slider').
# para mostrar o resultado na tela: st.header( date_slider ).

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais são as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'] )
# o traffic-options recebe o filtro de de multiseleção opções de tráfego

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Clebersc - Comunidade DS')

df1 = df1.loc[df1['Order_Date'] <= date_slider,:] #Filtro de data
#vicular os filtros (sidebar) aos gráficos (tab1, tab2, tab3), para que estes apresentem valores de acordo com os parâmetros aplicados na barra lateral.
#quando for usado o filtro st.sidebar.slider (valores guardados no date_slider), este comando seleciona as linhas que contenham datas menores ou iguais à que foi selecionada no filtro deslizante.

#Filtro de trânsito
df1 = df1.loc[ df1['Road_traffic_density'].isin( traffic_options ), : ] #esta consulta vai selecionar as linhas que contenham os tipos de tráfego indicados no filtro st.sidebar.multiselect. O comando .isin vai fazer o link entre esta consulta e o filtro, indicando que os tipos de tráfegos a serem considerados são os valores assumidos no filtro st.sidebar.multiselect.

# =======================================
# Layout no Streamlit
# ======================================= 
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Estratégica', 'Visão Geográfica'] ) #definiçao das tabs, que são os botões que vão abrir as páginas. Entre os parêntes, o st.tabs cria 3 abas para abrigar as diferentes visões. Elas serão guardadas dentro de 3 variáveis, em que cada uma é uma tab.

with tab1: #comando dentro da tab1, comando reservado do Python (cláusula) indicando que tudo que ficar identado abaixo da tab1 fará parte da Visão Gerencial.
    with st.container():#comando dentro do container, cria o 1º container para abrigar o gráfico dentro.
        st.markdown( '# Quantidade de pedidos por dia') #st.header equivale ao st.markdown.
        fig = order_metric( df1 )
        st.plotly_chart( fig, use_container_width=True ) 
#não é possível exibir o gráfico diretamente com o px, será usada função própria do st para executar o gráfico. Não é necessário comando para que o gráfico ocupe o tamanho exato do container.
        
    with st.container():#comando dentro do container, cria o 2º container para abrigar dois gráficos dentro.
        col1, col2 = st.columns(2) 
#separa o container em colunas. Entre os parêntes, o columns cria 2 colunas para abrigar os gráficos. Elas serão guardadas dentro de 2 variáveis, em que cada uma é uma coluna.

        with col1: #comando dentro da 1ª coluna
            st.markdown( '### Pedidos por tipo de tráfego')
            fig = traffic_order_share( df1 )
            st.plotly_chart( fig, use_container_width=True ) #comando para o gráfico ocupar o tamanho exato do container.
            
        with col2: #comando dentro da 2ª coluna
            st.markdown('### Pedidos por cidade e tipo de tráfego')
            fig = traffic_order_city ( df1 )
            st.plotly_chart(fig, use_container_width=True)
            
with tab2: #comando dentro da tab2
    with st.container(): #comando dentro do container, cria o 1º container para abrigar o gráfico dentro.
        st.markdown('# Pedidos por semana')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container(): #comando dentro do container, cria o 2º container para abrigar o gráfico dentro.
        st.markdown('# Pedidos por entregador por semana')
        fig = order_share_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)
        
with tab3: #comando dentro da tab3
    st.markdown('# Localização central de cada cidade por tipo de tráfego')
    country_maps (df1)