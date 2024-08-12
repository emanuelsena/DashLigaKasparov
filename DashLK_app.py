import streamlit as st
import pandas as pd
import io
import openpyxl
import chess.pgn
import chess
import chess.svg

# Inicializar as variáveis de estado da sessão
if 'selected_index' not in st.session_state:
    st.session_state.selected_index = 0
if 'window_width' not in st.session_state:
    st.session_state.window_width = st.session_state.get("window_width", 1000)
if 'move_index' not in st.session_state:
    st.session_state.move_index = 0
if 'show_pgn_df' not in st.session_state:
    st.session_state.show_pgn_df = False

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

# Inicializar df_exibido com o DataFrame original
df_exibido = df

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
    df_exibido = df_filtrado
else:
    vitorias_brancas = df[df["Resultado"].isin(["1 - 0", "1 - 0 w.o"])].shape[0]
    vitorias_negras = df[df["Resultado"].isin(["0 - 1", "0 - 1 w.o"])].shape[0]
    empates = df[df["Resultado"] == "1/2-1/2"].shape[0]
    derrotas_brancas = df[df["Resultado"].isin(["0 - 1", "0 - 1 w.o"])].shape[0]
    derrotas_negras = df[df["Resultado"].isin(["1 - 0", "1 - 0 w.o"])].shape[0]
    df_exibido = df

# Layout da tela principal
st.header("Estatísticas das Partidas")

# Exibir número de partidas filtradas / total
st.write(f"{len(df_exibido)} / {total_partidas} partidas")

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
st.dataframe(df_exibido)

# Botão para exportar df_exibido
csv = df_exibido.to_csv(index=False)
st.download_button(
    label="Exportar CSV",
    data=csv,
    file_name='dados.csv',
    mime='text/csv'
)

# Seleção da partida (abaixo do botão de exportar)
selected_index = st.selectbox("Selecione uma partida:", df_exibido.index, key="game_select")

# Obter o PGN da partida selecionada e tratar casos de dados faltantes
selected_pgn = df_exibido.loc[selected_index, "PGN"]

if selected_pgn and not (pd.isna(selected_pgn) or selected_pgn == ""):
    # Ler o jogo PGN usando chess.pgn (apenas se houver um PGN selecionado)
    game = chess.pgn.read_game(io.StringIO(selected_pgn))

    # Criar um DataFrame com os lances do PGN
    pgn_df = pd.DataFrame(columns=['Dados da Partida', 'Lance'])

    # Adicionar dados da partida à primeira linha do DataFrame
    pgn_df = pd.concat([pgn_df, pd.DataFrame({'Dados da Partida': [selected_pgn], 'Lance': ['']})], ignore_index=True)

    # Adicionar os lances ao DataFrame
    for i, move in enumerate(game.mainline_moves()):
        pgn_df = pd.concat([pgn_df, pd.DataFrame({'Dados da Partida': [''], 'Lance': [str(move)]})], ignore_index=True)

    # Definir o índice do DataFrame
    pgn_df.index = range(len(pgn_df))

    # Botão para mostrar/ocultar o DataFrame do PGN
    if st.button("Mostrar/Ocultar PGN"):
        st.session_state.show_pgn_df = not st.session_state.show_pgn_df

    # Exibir o DataFrame do PGN se o botão estiver ativado
    if st.session_state.show_pgn_df:
        st.dataframe(pgn_df)

    # Criar um tabuleiro de xadrez
    board = chess.Board()

    # Função para exibir o tabuleiro, a posição FEN e o número do lance
    def show_board(move_index):
        # Aplicar os movimentos até o índice selecionado
        board = chess.Board()  # Reiniciar o tabuleiro
        for i in range(move_index):
            move = pgn_df.loc[i + 1, 'Lance']
            if move:
                board.push_san(move)

        # Exibir o tabuleiro
        board_size = int(st.session_state.window_width * 0.5)
        svg = chess.svg.board(board=board, size=board_size)
        st.image(svg, use_column_width=True)

        # Exibir a posição FEN
        st.text(f"FEN: {board.fen()}")

        # Exibir o número do lance
        st.text(f"Lance: {move_index}")

    # Botões para navegar pelos lances
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Anterior"):
            if st.session_state.move_index > 0:
                st.session_state.move_index -= 1
    with col2:
        if st.button("Próximo ➡️"):
            if st.session_state.move_index < len(pgn_df) - 1:
                st.session_state.move_index += 1

    # Exibir o tabuleiro com base no lance selecionado
    show_board(st.session_state.move_index)