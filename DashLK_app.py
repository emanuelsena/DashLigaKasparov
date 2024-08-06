import streamlit as st
import pandas as pd

# Carregar dados do arquivo Excel
df = pd.read_excel('Liga Kasparov.xlsx', engine='openpyxl')

# Remover colunas sem nome do DataFrame original
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Imprimir os nomes das colunas para verificar (apenas para debug)
print(df.columns)

# Criar filtros no menu lateral
st.sidebar.header("Filtros")
filtro_nome = st.sidebar.text_input("Nome:")

# Contar partidas
total_partidas = df.shape[0]

# Contar vitórias e empates
vitorias_brancas = 0
vitorias_negras = 0
empates = 0
derrotas_brancas = 0
derrotas_negras = 0

if filtro_nome:
    df_filtrado = df[
        (df["Nome Brancas"].str.contains(filtro_nome, case=False)) | 
        (df["Nome Negras"].str.contains(filtro_nome, case=False))
    ]
    # Remover colunas sem nome do DataFrame filtrado
    df_filtrado = df_filtrado.loc[:, ~df_filtrado.columns.str.contains('^Unnamed')]

    # Corrigindo os contadores, incluindo "w.o"
    vitorias_brancas = df_filtrado[(df_filtrado["Nome Brancas"].str.contains(filtro_nome, case=False)) & ((df_filtrado["Resultado"] == "1 - 0") | (df_filtrado["Resultado"] == "1 - 0 w.o"))].shape[0]
    vitorias_negras = df_filtrado[(df_filtrado["Nome Negras"].str.contains(filtro_nome, case=False)) & ((df_filtrado["Resultado"] == "0 - 1") | (df_filtrado["Resultado"] == "0 - 1 w.o"))].shape[0]
    empates = df_filtrado[df_filtrado["Resultado"] == "1/2-1/2"].shape[0]
    derrotas_brancas = df_filtrado[(df_filtrado["Nome Brancas"].str.contains(filtro_nome, case=False)) & ((df_filtrado["Resultado"] == "0 - 1") | (df_filtrado["Resultado"] == "0 - 1 w.o"))].shape[0]
    derrotas_negras = df_filtrado[(df_filtrado["Nome Negras"].str.contains(filtro_nome, case=False)) & ((df_filtrado["Resultado"] == "1 - 0") | (df_filtrado["Resultado"] == "1 - 0 w.o"))].shape[0]
else:
    vitorias_brancas = df[df["Resultado"].isin(["1 - 0", "1 - 0 w.o"])].shape[0]
    vitorias_negras = df[df["Resultado"].isin(["0 - 1", "0 - 1 w.o"])].shape[0]
    empates = df[df["Resultado"] == "1/2-1/2"].shape[0]
    derrotas_brancas = df[df["Resultado"].isin(["0 - 1", "0 - 1 w.o"])].shape[0]
    derrotas_negras = df[df["Resultado"].isin(["1 - 0", "1 - 0 w.o"])].shape[0]

# Layout da tela principal
st.header("Estatísticas das Partidas")

# Cards em duas colunas
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Total de Partidas", total_partidas)
with col2:
    st.metric("Vitórias Brancas", vitorias_brancas)
with col3:
    st.metric("Vitórias Negras", vitorias_negras)
with col4:
    st.metric("Empates", empates)
with col5:
    st.metric("Derrotas Brancas", derrotas_brancas)
with col6:
    st.metric("Derrotas Negras", derrotas_negras)

# DataFrame em uma coluna
if filtro_nome:
    st.dataframe(df_filtrado)

    # Botão para exportar df_filtrado
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="Exportar CSV",
        data=csv,
        file_name='dados_filtrados.csv',
        mime='text/csv'
    )
else:
    st.dataframe(df)

    # Botão para exportar df
    csv = df.to_csv(index=False)
    st.download_button(
        label="Exportar CSV",
        data=csv,
        file_name='todos_os_dados.csv',
        mime='text/csv'
    )