import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

st.set_page_config(
    page_title="BIG SCORE JOGOS DO DIA",
    page_icon=":bar_chart:",
    layout="wide",
)
st.title(" O APP DO BIGODE ⚽")

st.markdown(
    """
    <span style="color: blue">**Faça aqui suas análises dos seus  jogos para suas estrátegia ⭐**</span><br>
    <span style="color: #FFC048">**  BIG   SCORE  **</span>  
    <span style="color: green">*Boas Análises!!!*</span>  
    """,
    unsafe_allow_html=True,
)


def load_data_jogos():
    data_jogos = pd.read_csv(
        r"C:\Users\Alexandre\OneDrive\Área de Trabalho\Projeto Fut\goalpyapp\dados_csv"
    )
    data_jogos = data_jogos[
        [

            "League",
            "Date",
            "Time",
            "Round",
            "Home",
            "Away",
            "FT_Odd_H",
            "FT_Odd_D",
            "FT_Odd_A",
            "FT_Odd_Over25",
            "FT_Odd_Under25",
            "FT_Odd_BTTS_Yes",
            "FT_Odd_BTTS_No",
            "Media_GM_H",
            "Media_GS_H",
            "Media_GM_H_10",
            "Media_GS_H_10",
            "Media_Total_2HT_H",
            "CV_Media_Total_2HT_H",
            "PPJ_H",
            "CV_Pontos_H",
            "Porc_Over05HT_Home",
            "Porc_Over15HT_Home",
            "Porc_Under05HT_Home",
            "Porc_Home_Win",
            "Porc_Home_Win_HT",
            "Porc_Over25FT_Home",
            "Porc_BTTS_Home",
            "Diferente_0x0_Home",
            "Media_GM_A",
            "Media_GS_A",
            "Media_GM_A_10",
            "Media_GS_A_10",
            "Media_Total_2HT_A",
            "CV_Media_Total_2HT_A",
            "PPJ_A",
            "CV_Pontos_A",
            "Porc_Over05HT_Away",
            "Porc_Over15HT_Away",
            "Porc_Under05HT_Away",
            "Porc_Away_Win",
            "Porc_Away_Win_HT",
            "Porc_Over25FT_Away",
            "Porc_BTTS_Away",
            "Diferente_0x0_Away",
            "xg_home",
            "xg_away",
            "xg_jogo",
        ]
    ]

    return data_jogos



df_jogos = load_data_jogos()

with st.sidebar:
    st.sidebar.header("Proximos Jogos")
    st.sidebar.image("goalpy_texture_00092.tif", use_column_width=True)

    with st.expander("Seleção Data"):
        sorted_unique_date = sorted(df_jogos.Date.unique())
        selected_date = st.multiselect("Date", sorted_unique_date, sorted_unique_date)
        if not selected_date:
            st.warning("Selecione pelo menos uma data para continuar.")
        else:
            df_jogos = df_jogos[df_jogos["Date"].isin(selected_date)]
            

# Define o valor mínimo e máximo iniciais com base na coluna "FT_Odd_H" do DataFrame
valor_min_home = float(df_jogos["FT_Odd_H"].min())
valor_max_home = float(df_jogos["FT_Odd_H"].max())
valor_min_draw = float(df_jogos["FT_Odd_D"].min())
valor_max_draw = float(df_jogos["FT_Odd_D"].max())
valor_min_away = float(df_jogos["FT_Odd_A"].min())
valor_max_away = float(df_jogos["FT_Odd_A"].max())
valor_min_over = float(df_jogos["FT_Odd_Over25"].min())
valor_max_over = float(df_jogos["FT_Odd_Over25"].max())

st.markdown(
    """
<span style="color: blue">**Filtro de  Odds**</span><br>
""",
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    valor_min_home, valor_max_home = st.slider(
        "Casa",
        float(df_jogos["FT_Odd_H"].min()),
        float(df_jogos["FT_Odd_H"].max()),
        (valor_min_home, valor_max_home),
        step=0.01,
    )
with col2:
    valor_min_draw, valor_max_draw = st.slider(
        "Empate",
        float(df_jogos["FT_Odd_D"].min()),
        float(df_jogos["FT_Odd_D"].max()),
        (valor_min_draw, valor_max_draw),
        step=0.01,
    )
with col3:
    valor_min_away, valor_max_away = st.slider(
        "Fora",
        float(df_jogos["FT_Odd_A"].min()),
        float(df_jogos["FT_Odd_A"].max()),
        (valor_min_away, valor_max_away),
        step=0.01,
    )
with col4:
    valor_min_over, valor_max_over = st.slider(
        "Over 2.5",
        float(df_jogos["FT_Odd_Over25"].min()),
        float(df_jogos["FT_Odd_Over25"].max()),
        (valor_min_over, valor_max_over),
        step=0.01,
    )


df_filtrado = df_jogos.query(
    "@valor_min_home <= FT_Odd_H <= @valor_max_home and @valor_min_draw <= FT_Odd_D <= @valor_max_draw and\
                              @valor_min_away <= FT_Odd_A <= @valor_max_away and @valor_min_over <= FT_Odd_Over25 <= @valor_max_over"
)

st.subheader("Jogos do Dia")
st.markdown(f"Total jogos para o dia  de Hoje : {len(df_filtrado)} jogos")
st.dataframe(df_filtrado)
st.markdown("""---""") 
#.......................................................................
#.......................................................................

df_over_ht = df_jogos.copy()
df_over_ht15 = df_jogos.copy()
df_over_25 = df_jogos.copy()

#........................................................................

df_2tmp = df_jogos.copy()
df_1x = df_jogos.copy()
df_home_win = df_jogos.copy()
df_away_win = df_jogos.copy() 


#.......................................................................

tab1, tab2 = st.tabs(["Overs", "Outras Estrátegias"])
with tab1:
    filtro_Over_ht = (
        (df_over_ht.Porc_Over05HT_Home >=60)&
        (df_over_ht.Porc_Over05HT_Away>= 60)&
        (df_over_ht.xg_jogo>= 2.5)&
        (df_over_ht.Diferente_0x0_Home>= 100)&
        (df_over_ht.Diferente_0x0_Away>= 100)        
    )
    df_over_ht = df_over_ht[filtro_Over_ht]
    st.subheader("Tendência Over 05 HT")
    st.markdown(f"Total jogos para o dia  de Hoje : {len(df_over_ht)} jogos")
    st.dataframe(df_over_ht)
    
    filtro_Over_ht15 = (
        (df_over_ht15.Porc_Over15HT_Home >=50)&
        (df_over_ht15.Porc_Over15HT_Away>= 50)&
        (df_over_ht15.xg_jogo>= 2.5)&
        (df_over_ht15.Diferente_0x0_Home>= 100)&
        (df_over_ht15.Diferente_0x0_Away>= 100)  
    )
    df_over_ht15 = df_over_ht15[filtro_Over_ht15]
    st.subheader("Tendência Over 15 HT")
    st.markdown(f"Total jogos para o dia  de Hoje : {len(df_over_ht15)} jogos")
    st.dataframe(df_over_ht15)    
    

    filtro_Over_25 = (
        (df_over_25.Porc_Over25FT_Home >=55)&
        (df_over_25.Porc_Over25FT_Away>= 55)&
        (df_over_25.xg_jogo>= 2.5)&
        (df_over_25.Diferente_0x0_Home>= 100)&
        (df_over_25.Diferente_0x0_Away>= 100)       
    )
    df_over_25 = df_over_25[filtro_Over_25]
    st.subheader("Tendência Over 25 FT")
    st.markdown(f"Total jogos para o dia  de Hoje : {len(df_over_25)} jogos")
    st.dataframe(df_over_25)
    

    
with tab2:

    filtro_2tmp = (
    (df_2tmp.xg_jogo >=2.4)&
    (df_2tmp.Media_Total_2HT_H >=0.9)&
    (df_2tmp.Media_Total_2HT_A >=0.8)&
    (df_2tmp.CV_Media_Total_2HT_H <=0.5)&
    (df_2tmp.CV_Media_Total_2HT_A <=0.6)&
    (df_2tmp.Diferente_0x0_Home>= 100)&
    (df_2tmp.Diferente_0x0_Away>= 100) 
   )
    
    df_2tmp = df_2tmp[filtro_2tmp]
    st.subheader("Tendência Gols  no Segundo Tempo")
    st.markdown("""---""") 
    st.markdown("""
                Para este filtro, quando o placar ao final do primeiro tempo é igual a 0 x 0, 0 x 1, 1 x 1, 1 x 0 , 1 x 2 ou 2 x 1 desde que se tenhamos um time em desvantagem ele esteja corendo atras do resultado
                ,consideramos buscar uma aposta em gols asiáticos com um intervalo de tempo mais longo,dependendo da dinâmica da partida e do desempenho das equipes. A nossa meta é encontrar oportunidades com odds mínimas de pelo menos @1.60 no Over limite e @2.00 para o asiático.
                """)
    st.markdown(f"Total jogos para o dia  de Hoje : {len(df_2tmp)} jogos")
    st.dataframe(df_2tmp)
    st.markdown("""---""") 