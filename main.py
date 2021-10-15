#coding:utf-8
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pydeck as pdk

st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_option.allow_output_mutation=True
st.set_option.token= 'pk.eyJ1IjoiZGlvZ29kb2kiLCJhIjoiY2tzamZ6MHAxMmRxZzJxb215MjMwcXU5MSJ9.TPC7ytOmDICm-GyF4fsWSQ'
st.title("""
 A educação nas prisões no estado de São Paulo: a responsabilidade da universidade pública.""")
st.subheader('Distribuição das Universidades e Unidades Prisionais')
data_load_state = st.text('Loading data...')
#Unidades prisionais
# @st.cache
def load_unidades_prisionais():
    path ='UNIDADESPRISIONAIS.csv'
    df_unidades_prisionais = pd.read_csv(path)
    df_peni = df_unidades_prisionais.loc[df_unidades_prisionais['colors']=='green']
    df_CDP = df_unidades_prisionais.loc[df_unidades_prisionais['colors']=='yellow']
    df_CR = df_unidades_prisionais.loc[df_unidades_prisionais['colors']=='black']
    df_CPP = df_unidades_prisionais.loc[df_unidades_prisionais['colors']=='gray']
    df_US = df_unidades_prisionais.loc[df_unidades_prisionais['colors']=='purple']
    return df_peni, df_CDP, df_CR,df_CPP, df_US
df_peni, df_CDP, df_CR,df_CPP, df_US= load_unidades_prisionais()
# df_unidades_prisionais

#CDPS
@st.cache
def load_CDPS():
    path = 'CDPS.csv'
    df_CDPS = pd.read_csv(path)
    return df_CDPS

df_CDPS = load_CDPS()
# df_CDPS

#UNIVERSIDADES
# @st.cache
def load_universidades():
    path = 'Universidade.csv'
    df_universidades = pd.read_csv(path)
    return df_universidades
df_universidades = load_universidades()
# df_universidades

meso = gpd.read_file("SP_Mesorregioes_2020/SP_Mesorregioes_2020.shp")
meso['colors'] = ['#EAEAE0'for i in range(15)]

data_load_state.text("Done!")

def meso_settings(mesorregiao):
    if len(mesorregiao)== 0:
        return ['#A9A9A9' for i in range(15)]    
    lista_vazia = ['white' for i in range(15)]
    for i in mesorregiao:
        value = meso[meso['NM_MESO'] == i].index.values      
        lista_vazia[int(value[0])] = '#A9A9A9'      
    return lista_vazia
        
# #Sidebar
populacao=st.sidebar.slider('População Carcerária',int(df_CDPS['TOTAL'].max()),int(df_CDPS['TOTAL'].min()))
mesorregiao = st.sidebar.multiselect("Selecione uma mesorregião", (meso['NM_MESO']))
unidades = st.sidebar.multiselect("Selecione a Unidade",df_universidades['UNIDADE'].unique())
universidades = st.sidebar.multiselect("Selecione a Universidade",df_universidades.loc[df_universidades['UNIDADE'].isin(unidades)].NOME)
unidade_prisional = st.sidebar.multiselect("Selecione uma unidade prisional",["CR","CPP","CDP","Penintenciária","Centro de Saúde"])

def universidades_settings(unidades):
    if len(unidades) == 0:
        return df_universidades
    unidade = df_universidades.loc[df_universidades.UNIDADE.isin(unidades)]
    return unidade

#Mapa com settings
meso['colors'] = meso_settings(mesorregiao) 
def settings(total,unidades):
    filtred_CDPs = df_CDPS.loc[df_CDPS.TOTAL >= total]
    filtred_universidade = universidades_settings(unidades)    
    return filtred_universidade, filtred_CDPs

def mapa_settings(universidade, filtred_universidade,filtred_CDP):
    if len(universidades) == 0:
        pass
    else:
        filtred_universidade = filtred_universidade.loc[filtred_universidade.NOME.isin(universidade)]
    filtred_universidade = filtred_universidade[['lat','lon','ENDERECO','NOME']]
    filtred_CDP = filtred_CDP[['lat','lon','ENDERECO','NOME','TOTAL']]
    return filtred_universidade,filtred_CDP

filtred_universidade, filtred_CDPs = settings(populacao,unidades)
map_universidade, map_cdps = mapa_settings(universidades,filtred_universidade,filtred_CDPs)

coords_universidades = gpd.GeoDataFrame(map_universidade, geometry=gpd.points_from_xy(map_universidade.lon,map_universidade.lat))

ax = meso.plot(color = meso['colors'], edgecolor='k')
plt.axis("off")
coords_universidades.plot(ax=ax, color = filtred_universidade['colors'], label= "Universidades")
if len(unidade_prisional) ==0:    
    coords_peni = gpd.GeoDataFrame(df_peni, geometry=gpd.points_from_xy(df_peni.lon,df_peni.lat))
    coords_peni.plot(ax=ax, color = coords_peni['colors'], label= "Penintenciária")
    
    coords_CDP = gpd.GeoDataFrame(df_CDP, geometry=gpd.points_from_xy(df_CDP.lon,df_CDP.lat))
    coords_CDP.plot(ax=ax, color = coords_CDP['colors'], label= "CDP")
    
    coords_CR = gpd.GeoDataFrame(df_CR, geometry=gpd.points_from_xy(df_CR.lon,df_CR.lat))
    coords_CR.plot(ax=ax, color = coords_CR['colors'], label= "CR")
    
    coords_CPP = gpd.GeoDataFrame(df_CPP, geometry=gpd.points_from_xy(df_CPP.lon,df_CPP.lat))
    coords_CPP.plot(ax=ax, color = coords_CR['colors'], label= "CPP")
    
    coords_US = gpd.GeoDataFrame(df_US, geometry=gpd.points_from_xy(df_US.lon,df_US.lat))
    coords_US.plot(ax=ax, color = coords_US['colors'], label= "Centro de Saúde")
else:
    for i in unidade_prisional:
        if "Penintenciária" in i:            
            coords_peni = gpd.GeoDataFrame(df_peni, geometry=gpd.points_from_xy(df_peni.lon,df_peni.lat))
            coords_peni.plot(ax=ax, color = coords_peni['colors'], label= "Penintenciária")
            # lista.append('green')
        elif 'CDP' in i:            
            coords_CDP = gpd.GeoDataFrame(df_CDP, geometry=gpd.points_from_xy(df_CDP.lon,df_CDP.lat))
            coords_CDP.plot(ax=ax, color = coords_CDP['colors'], label= "CDP")
            # lista.append('yellow')
        elif 'CR' in i:           
            coords_CR = gpd.GeoDataFrame(df_CR, geometry=gpd.points_from_xy(df_CR.lon,df_CR.lat))
            coords_CR.plot(ax=ax, color = coords_CR['colors'], label= "CR")
            # lista.append('black')
        elif 'CPP' in i:            
            coords_CPP = gpd.GeoDataFrame(df_CPP, geometry=gpd.points_from_xy(df_CPP.lon,df_CPP.lat))
            coords_CPP.plot(ax=ax, color = coords_CR['colors'], label= "CPP")
            # lista.append('gray')
        else:            
            coords_US = gpd.GeoDataFrame(df_US, geometry=gpd.points_from_xy(df_US.lon,df_US.lat))
            coords_US.plot(ax=ax, color = coords_US['colors'], label= "CPP")
            # lista.append('purple')

plt.legend()
st.pyplot()

st.subheader(""" Distribuição das CDPS e UNIVERSIDADES
""")

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=-23.53280,
        longitude=-46.63704,
        zoom=6,
        pitch=50,
        min_zoom=6,
        max_zoom= 10,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data = map_cdps,
            get_position = ['lon','lat'],
            get_fill_color=[0, 0, 255,255],
            elevation_scale=10,
            get_elevation=['TOTAL'],
            pickable=True,
            extruded=True,
            
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data = map_universidade,
            get_position = ['lon','lat'],
            get_fill_color=[255, 0, 0, 255],
            get_radius=1000,
            pickable=True,
            extruded=True,            
        ),
    ],
            tooltip= {"html": "<b>{NOME} <br/> <b> {ENDERECO}",
             "style": {"backgroundColor": "steelblue","color": "white"}},
            
    
    ))

if st.sidebar.checkbox('Mostrar dados das universidades'):
    st.subheader('Dados das Universidades')
    st.write(filtred_universidade[['NOME','UNIDADE','ENDERECO','CONTATO','TELEFONE']])
    st.subheader('Dados CDPs')

if st.sidebar.checkbox('Mostrar dados das CDPs'):   
    municipio = st.multiselect('Selecione um município',filtred_CDPs['ENDERECO'].unique())
    if st.checkbox('Mostrar tabela das CDPs'):
        st.write('Tabela CDPs')
        if len(municipio)==0:
            st.write(filtred_CDPs.iloc[:,2:14])
        else:
            dados= filtred_CDPs.loc[filtred_CDPs.ENDERECO.isin(municipio)]
            st.write(dados.iloc[:,2:14])
    if len(municipio) == 0:
        st.bar_chart(filtred_CDPs.iloc[:,5:14].rename(index=filtred_CDPs.NOME))
    else:
        chart_data = filtred_CDPs[filtred_CDPs.ENDERECO.isin(municipio)].rename(index=filtred_CDPs.NOME)
        st.bar_chart(chart_data.iloc[:,5:14])

    
footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by  <a style='display: block; text-align: center;' href="https://www.linkedin.com/in/godoid/" target="_blank">Diogo Henrique Godoi</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
