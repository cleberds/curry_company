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

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍴', layout='wide' )#expandir o gráfico
# =======================================
# Funções
# =======================================
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


def distance( df1, fig ):
    coluna1 = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['Distance'] = (df1.loc[:,coluna1]
                          .apply( lambda x: haversine(
                                        (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))

    if fig==False:
        average_distance = np.round( df1['Distance'].mean(), 2 )
        return average_distance
    
    else:
        average_distance = df1.loc[:, ['City','Distance']].groupby ('City').mean().reset_index()
        fig = go.Figure( data=[ go.Pie( labels=average_distance['City'], values=average_distance['Distance'], pull=[0, 0.2, 0])]) #usando biblioteca go. No go.Figure, informe os dados, que, no caso, se referem a gráfico de pizza: Cidades e valores das distâncias médias. Pull indica qual pedaço da pizza será puxado e quanto.
        return fig


def avg_std (df1, fest, op):
    '''
    Esta função calcula o tempo médio e o desvio-padrão do tempo de entrega.
    Parâmetros:
        Input:
            - df: dataframe com os dados necessários para o cálculo;
            - op: tipo de operação que precisa ser calculada;
                - 'avg_time': calcula o tempo médio;
                - 'std_time': calcula o desvio-padrão do tempo.
        Output:
            - df: Dataframe com 2 colunas e 1 linha.
    '''
    coluna = ['Time_taken(min)','Festival']
    consulta = np.round( df1.loc[:,coluna].groupby('Festival').agg({'Time_taken(min)':['mean','std']}), 2 )
    consulta.columns = ['avg_time', 'std_time']
    consulta = consulta.reset_index()
    mean_std_yes_no = consulta.loc[(consulta['Festival'] == fest), op ]
    return mean_std_yes_no


def avg_std_graph ( df1 ):
    coluna3 = ['Time_taken(min)','City']
    consulta3 = df1.loc[:,coluna3].groupby('City').agg({'Time_taken(min)':['mean','std']})
    consulta3.columns = ['avg_time', 'std_time']
    consulta3 = consulta3.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name = 'Control', x = consulta3['City'], y = consulta3['avg_time'], error_y = dict( type = 'data', array = consulta3[ 'std_time'])))
    fig.update_layout(barmode = 'group')
    return fig


def avg_std_traffic (df1):
    coluna5 = ['Time_taken(min)','City','Road_traffic_density']
    consulta5 = (df1.loc[:,coluna5]
             .groupby(['City','Road_traffic_density'])
             .agg({ 'Time_taken(min)':['mean','std']}))
    consulta5.columns = ['avg_time','std_time']
    consulta5 = consulta5.reset_index()
    fig = px.sunburst( consulta5, path=['City', 'Road_traffic_density'], values='avg_time', 
                      color='std_time', 
                      color_continuous_scale='RdBu', 
                      color_continuous_midpoint=np.average(consulta5['std_time']))
    return fig
        

# importar dataset
df = pd.read_csv('dataset/train.csv') #no google colab usa-se o 'cl.files.upload()' para subir o arquivo da máquina para as nuvens. Aqui basta indicar o caminho onde está o arquivo.

# cleaning code
df1 = clean_code ( df )

# =======================================
# Barra lateral
# ======================================= 
#a construção do layout é baseado no arquivo 'planejamento_dashboard.drawio', e feito no caminho 'docs => API reference'
#os comandos são construídos no Python File (visao_empresa.py), o terminal compila os comandos e executa em um navegador que será aberto automaticamente.
#a cada etapa de estruturação no terminaL deve ser rodado o comando 'streamlit run visao_empresa.py', que executará as alterações do arquivo fonte diretamente no navegador, deixando o terminal ocupado de modo ininterrupto. Para parar o run e possibilitar executar mais comandos, acionar o Ctrl+C no terminal. 
#no navegador gerado pelo streamlit run, clicar no 'always rerun' para que seja reconhecida e apresentada automaticamente na tela qualquer alteração nos construção dos comandos do arquivo Python File. 

st.header('Marketplace - Visão Restaurantes') #comando cria um título na região macro ('docs => API reference => Text elements => st.header')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('Entregadores & Distância')
            delivery_unique = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos', delivery_unique)

            st.markdown('''---''')

            average_distance = distance(df1, fig=False)
            col1.metric('Distância média restaurante - destino', average_distance)
            

        with col2:
            st.markdown('Tempo de entrega com Festival')
            mean_std_yes_no = avg_std (df1, 'Yes', 'avg_time')
            col2.metric('Média - Festival', mean_std_yes_no)

            st.markdown('''---''')

            mean_std_yes_no = avg_std (df1, 'Yes', 'std_time')
            col2.metric('Desvio-padrão - Festival', mean_std_yes_no)

        with col3:
            st.markdown('Tempo de entrega sem Festival')
            mean_std_yes_no = avg_std (df1, 'No','avg_time')
            col3.metric('Média - sem Festival', mean_std_yes_no)
            
            st.markdown('''---''')
            
            mean_std_yes_no = avg_std (df1, 'No','std_time')
            col3.metric('Desvio-padrão - sem Festival', mean_std_yes_no)
 
    with st.container():
        st.markdown('''---''')
        col1, col2 = st.columns(2)

        with col1:
            fig = avg_std_graph ( df1 )
            st.plotly_chart(fig, use_container_width=True )        
             
        with col2:
            coluna4 = ['Time_taken(min)','City','Type_of_order']
            consulta4 = df1.loc[:,coluna4].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std'] })
            consulta4.columns = ['avg_time', 'std_time']
            consulta4 = consulta4.reset_index()
            st.dataframe(consulta4, use_container_width=True )
            
    with st.container():
        st.markdown('''---''')
        st.title('Distribuição da distância e tempo')
        col1, col2 = st.columns(2)

        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True )

        with col2:
            fig = avg_std_traffic (df1)
            st.plotly_chart( fig )