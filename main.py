#coding:utf-8
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_option.allow_output_mutation=True

st.title("""
 A educação nas prisões no estado de São Paulo: a responsabilidade da universidade pública.""")
st.subheader('Distribuição das Universidades e Unidades Prisionais')
data_load_state = st.text('Carregando dados..')
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
    return df_unidades_prisionais,df_peni, df_CDP, df_CR,df_CPP, df_US
df_unidades_prisionais,df_peni, df_CDP, df_CR,df_CPP, df_US= load_unidades_prisionais()
# df_unidades_prisionais

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

data_load_state.text("Dados carregados!")

def meso_settings(mesorregiao):
    if len(mesorregiao)== 0:
        return ['#D8D8D8' for i in range(15)]    
    lista_vazia = ['white' for i in range(15)]
    for i in mesorregiao:
        value = meso[meso['NM_MESO'] == i].index.values      
        lista_vazia[int(value[0])] = '#D8D8D8'          
    return lista_vazia
        
# #Sidebar
mesorregiao = st.sidebar.multiselect("Selecione uma mesorregião", (meso['NM_MESO']))
unidades = st.sidebar.multiselect("Selecione a Unidade da universidade",df_universidades['UNIDADE'].unique())
universidades = st.sidebar.multiselect("Selecione a Universidade",df_universidades.loc[df_universidades['UNIDADE'].isin(unidades)].NOME)
unidade_prisional = st.sidebar.multiselect("Selecione o tipo da unidade prisional",["CR","CPP","CDP","Penintenciária","Centro de Saúde"])


def filtro_meso(mesorregiao,universidades):
    lista_pontos = []
    lista_poly = meso[meso['NM_MESO'].isin(mesorregiao)].geometry
    for x in lista_poly:            
        for point in universidades['geometry']:
            if x.contains(point):
                lista_pontos.append(point)
    return lista_pontos   

def universidades_settings(unidades):
    if len(unidades) == 0:
        return df_universidades
    unidade = df_universidades.loc[df_universidades.UNIDADE.isin(unidades)]
    return unidade

#Mapa com settings
 
def settings(unidades, mesorregiao):
    filtred_universidade = universidades_settings(unidades)
    if len(mesorregiao) == 0:
        return filtred_universidade
    else:
        coordenadas = gpd.GeoDataFrame(filtred_universidade, geometry=gpd.points_from_xy(filtred_universidade.lon,filtred_universidade.lat))
        lista_pontos = filtro_meso(mesorregiao,coordenadas)
        filtred_universidade = filtred_universidade[filtred_universidade['geometry'].isin(lista_pontos)]   
    return filtred_universidade

def mapa_settings(universidade, filtred_universidade):
    if len(universidades) == 0:
        pass
    else:
        filtred_universidade = filtred_universidade.loc[filtred_universidade.NOME.isin(universidade)]
    filtred_universidade = filtred_universidade[['lat','lon','ENDERECO','NOME']]
    
    return filtred_universidade

filtred_universidade = settings(unidades,mesorregiao)
map_universidade = mapa_settings(universidades,filtred_universidade)

coords_universidades = gpd.GeoDataFrame(map_universidade, geometry=gpd.points_from_xy(map_universidade.lon,map_universidade.lat))

meso['colors']= meso_settings(mesorregiao)


ax = meso.plot(color = meso['colors'], edgecolor='k')
plt.axis("off")
coords_universidades.plot(ax=ax, color = filtred_universidade['colors'], label= "Universidades")
if len(unidade_prisional) == 0:
    coords_unidades_prisionais = gpd.GeoDataFrame(df_unidades_prisionais, geometry=gpd.points_from_xy(df_unidades_prisionais.lon,df_unidades_prisionais.lat))
    if len(mesorregiao) == 0:    
        coords_unidades_prisionais.plot(ax=ax, color = "blue", label= "Unidades Prisionais",marker="*")
    else:
        lista_pontos = filtro_meso(mesorregiao,coords_unidades_prisionais)
        coords_unidades_prisionais = coords_unidades_prisionais[coords_unidades_prisionais['geometry'].isin(lista_pontos)]
        coords_unidades_prisionais.plot(ax=ax, color = "blue", label= "Unidades Prisionais",marker="*")    
else:
    for i in unidade_prisional:
        if "Penintenciária" in i:
            coords_peni = gpd.GeoDataFrame(df_peni, geometry=gpd.points_from_xy(df_peni.lon,df_peni.lat))
            if len(mesorregiao) == 0:            
                coords_peni.plot(ax=ax, color = coords_peni['colors'], label= "Penintenciária", marker=".")
            else:
                lista_pontos = filtro_meso(mesorregiao,coords_peni)
                coords_peni = coords_peni[coords_peni['geometry'].isin(lista_pontos)]
                coords_peni.plot(ax=ax, color = coords_peni['colors'], label= "Penintenciária", marker=".")
            # lista.append('green')
        elif 'CDP' in i:
            coords_CDP = gpd.GeoDataFrame(df_CDP, geometry=gpd.points_from_xy(df_CDP.lon,df_CDP.lat))
            if len(mesorregiao) == 0:            
                coords_CDP.plot(ax=ax, color = coords_CDP['colors'], label= "CDP",marker="<")
            else:
                lista_pontos = filtro_meso(mesorregiao,coords_CDP)
                coords_CDP = coords_CDP[coords_CDP['geometry'].isin(lista_pontos)]
                coords_CDP.plot(ax=ax, color = coords_CDP['colors'], label= "CDP",marker="<")
            # lista.append('yellow')
        elif 'CR' in i:
            coords_CR = gpd.GeoDataFrame(df_CR, geometry=gpd.points_from_xy(df_CR.lon,df_CR.lat))
            if len(mesorregiao) == 0:           
                coords_CR.plot(ax=ax, color = coords_CR['colors'], label= "CR",marker='v')
            else:
                lista_pontos = filtro_meso(mesorregiao,coords_CR)
                coords_CR = coords_CR[coords_CR['geometry'].isin(lista_pontos)]
                coords_CR.plot(ax=ax, color = coords_CR['colors'], label= "CR",marker='v')
            # lista.append('black')
        elif 'CPP' in i:
            coords_CPP = gpd.GeoDataFrame(df_CPP, geometry=gpd.points_from_xy(df_CPP.lon,df_CPP.lat))
            if len(mesorregiao) == 0:            
                coords_CPP.plot(ax=ax, color = coords_CPP['colors'], label= "CPP",marker=">")
            else:
                lista_pontos = filtro_meso(mesorregiao,coords_CPP)
                coords_CPP = coords_CPP[coords_CPP['geometry'].isin(lista_pontos)]
                coords_CPP.plot(ax=ax, color = coords_CPP['colors'], label= "CPP",marker=">")
            # lista.append('gray')
        else:
            coords_US = gpd.GeoDataFrame(df_US, geometry=gpd.points_from_xy(df_US.lon,df_US.lat))
            if len(mesorregiao) == 0:            
                coords_US.plot(ax=ax, color = coords_US['colors'], label= "Centro de Saúde",marker="*")
            else:
                lista_pontos = filtro_meso(mesorregiao,coords_US)
                coords_US = coords_US[coords_US['geometry'].isin(lista_pontos)]
                coords_US.plot(ax=ax, color = coords_US['colors'], label= "Centro de Saúde",marker="*")
            # lista.append('purple')

plt.legend()
st.pyplot()
st.markdown('CDP: Centro de Detenção Provisório <br />'
        'CR: Centro de Ressocialização <br />'
        'CPP:',unsafe_allow_html= True )


st.subheader('Dados das Universidades')
st.write(filtred_universidade[['NOME','UNIDADE','ENDERECO','CONTATO','TELEFONE']])


    
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
