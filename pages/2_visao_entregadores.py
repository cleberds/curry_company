# importar bibliotecas
import pandas as pd #se o terminal não reconhecer o pandas, o pacote deve ser instalado no terminal (pip install pandas) 
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image #biblioteca de edição de imagens

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide' )#expandir o gráfico
#----------------------------------------
# Funções
#----------------------------------------
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

def top_delivers ( df1, top_ascending ):
    consulta = ( df1[['Delivery_person_ID','Time_taken(min)','City']]
                .groupby(['City','Delivery_person_ID'])
                .mean()
                .sort_values(['City','Time_taken(min)'],ascending = top_ascending)
                .reset_index() )
    filtro1 = consulta[(consulta['City'] == 'Metropolitian')].head(10)
    filtro2 = consulta[(consulta['City'] == 'Urban')].head(10)
    filtro3 = consulta.loc[(consulta['City'] == 'Semi-Urban'),:].head(10)
    consulta_concat = pd.concat([filtro1,filtro2,filtro3]).reset_index(drop=True)
    return consulta_concat

# importar dataset
df = pd.read_csv('dataset/train.csv') #no google colab usa-se o 'cl.files.upload()' para subir o arquivo da máquina para as nuvens. Aqui basta indicar o caminho onde está o arquivo.

#cleaning dataset
df1 = clean_code (df)

# =======================================
# Barra lateral
# ======================================= 
#a construção do layout é baseado no arquivo 'planejamento_dashboard.drawio', e feito no caminho 'docs => API reference'
#os comandos são construídos no Python File (visao_empresa.py), o terminal compila os comandos e executa em um navegador que será aberto automaticamente.
#a cada etapa de estruturação no terminaL deve ser rodado o comando 'streamlit run visao_empresa.py', que executará as alterações do arquivo fonte diretamente no navegador, deixando o terminal ocupado de modo ininterrupto. Para parar o run e possibilitar executar mais comandos, acionar o Ctrl+C no terminal. 
#no navegador gerado pelo streamlit run, clicar no 'always rerun' para que seja reconhecida e apresentada automaticamente na tela qualquer alteração nos construção dos comandos do arquivo Python File. 

st.header('Marketplace - Visão Entregadores') #comando cria um título na região macro ('docs => API reference => Text elements => st.header')

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
tab1, tab2, tab3 = st.tabs (['Visão Gerencial', '_', '_'])
with tab1:
    with st.container():
        st.title('Métricas gerais')
        col1, col2, col3, col4 = st.columns (4, gap = 'large')
        with col1:
            maior_idade = df1['Delivery_person_Age'].max()
            st.metric('Maior idade', maior_idade )

        with col2:
            menor_idade = df1['Delivery_person_Age'].min()
            st.metric( 'Menor idade', menor_idade )

        with col3:
            melhor_condicao = df1['Vehicle_condition'].max()
            st.metric('Veic melhor condição', melhor_condicao )
            
        with col4:
            pior_condicao = df1['Vehicle_condition'].min()
            st.metric('Veic pior condicao', pior_condicao )

    with st.container():
        st.markdown('''---''')
        st.title("Avaliação média")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Média por entregador')
            rating = ( df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                    .groupby('Delivery_person_ID')
                    .mean()
                    .reset_index()
                    .sort_values('Delivery_person_Ratings',ascending=False) )
            rating.columns = ['Delivery_person_ID','rating_médio']
            st.dataframe(rating)
            
        with col2:
            st.markdown('##### Média por trânsito')
            #Agregação da média e do desvio padrão das avaliações por tipo de tráfego
            mean_std_traf = (df1[['Delivery_person_Ratings','Road_traffic_density']]
                        .groupby('Road_traffic_density')
                        .agg({'Delivery_person_Ratings' : ['mean','std']}))
            mean_std_traf.columns = ['média', 'desvio-padrão']
            mean_std_traf = mean_std_traf.reset_index()
            st.dataframe(mean_std_traf)
            
            st.markdown('##### Média por condição climática')
            mean_std_wea = (df1[['Weatherconditions', 'Delivery_person_Ratings']]
                        .groupby('Weatherconditions')
                        .agg( { 'Delivery_person_Ratings' : ['mean','std']}))
            mean_std_wea.columns = ['média', 'desvio-padrão']
            mean_std_wea = mean_std_wea.reset_index()
            st.dataframe(mean_std_wea)
            
    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top 10 entregadores rápidos')
            consulta_concat = top_delivers ( df1, top_ascending=True )
            st.dataframe(consulta_concat)
            
        with col2:
            st.markdown('##### Top 10 entregadores lentos')
            consulta_concat = top_delivers (df1, top_ascending=False)
            st.dataframe(consulta_concat)