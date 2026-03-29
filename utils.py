"""
Utility functions for the Digital Twin Goalkeeper Dashboard.
Handles data loading, filtering, and theme management.
"""
import pandas as pd
import streamlit as st

# Theme color definitions for Light and Dark modes
THEMES = {
    "light": {
        "bg": "#ffffff",
        "text": "#000000",
        "sidebar_bg": "linear-gradient(#1e2129, #0e1117)",
        "sidebar_text": "#ffffff",
        "header_title": "#000000",
        "header_subtitle": "#444444",
        "subtitle": "#666666",
        "metric_label": "#666666",
        "filter_row_bg": "#dee2e6",
        "filter_row_border": "#e6e9ef",
        "filter_title": "#2c3e50",
        "popover_bg": "#edf2f7",
        "popover_text": "#333333",
        "popover_border": "#cbd5e0",
        "popover_hover_bg": "#e2e8f0",
        "hr": "rgba(0, 0, 0, 0.1)",
        "nav_sidebar_bg": "#ffffff",
        "nav_sidebar_text": "#4fa6ff",
        "toggle_bg": "#000000",
        "toggle_handle": "#ffffff"
    },
    "dark": {
        "bg": "#0e1117",
        "text": "#ffffff",
        "sidebar_bg": "linear-gradient(#1e2129, #0e1117)",
        "sidebar_text": "#ffffff",
        "header_title": "#ffffff",
        "header_subtitle": "#cccccc",
        "subtitle": "#ffffff",
        "metric_label": "#aaaaaa",
        "filter_row_bg": "#1e2129",
        "filter_row_border": "#2d3139",
        "filter_title": "#ffffff",
        "popover_bg": "#1e2129",
        "popover_text": "#ffffff",
        "popover_border": "#2d3139",
        "popover_hover_bg": "#2d3139",
        "hr": "rgba(255, 255, 255, 0.1)",
        "nav_sidebar_bg": "#1e2129",
        "nav_sidebar_text": "#ffffff",
        "toggle_bg": "#000000",
        "toggle_handle": "#ffffff"
    }
}

def carregar_css(theme_key="light", css_file="style.css"):
    """
    Injects custom CSS and dynamic theme variables into the Streamlit app.
    """
    try:
        colors = THEMES.get(theme_key, THEMES["light"])
        css_vars = f"""
        <style>
        :root {{
            --bg-color: {colors['bg']};
            --text-color: {colors['text']};
            --sidebar-bg: {colors['sidebar_bg']};
            --sidebar-text: {colors['sidebar_text']};
            --main-header-title: {colors['header_title']};
            --main-header-subtitle: {colors['header_subtitle']};
            --subtitle-visualizacao: {colors['subtitle']};
            --metric-label: {colors['metric_label']};
            --filter-row-bg: {colors['filter_row_bg']};
            --filter-row-border: {colors['filter_row_border']};
            --filter-title: {colors['filter_title']};
            --popover-bg: {colors['popover_bg']};
            --popover-text: {colors['popover_text']};
            --popover-border: {colors['popover_border']};
            --popover-hover-bg: {colors['popover_hover_bg']};
            --hr-color: {colors['hr']};
            --nav-sidebar-bg: {colors['nav_sidebar_bg']};
            --nav-sidebar-text: {colors['nav_sidebar_text']};
            --toggle-bg: {colors['toggle_bg']};
            --toggle-handle: {colors['toggle_handle']};
        }}
        </style>
        """
        st.markdown(css_vars, unsafe_allow_html=True)
        with open(css_file, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Ficheiro {css_file} não encontrado.")

@st.cache_data
def carregar_dados(csv_path="data/dataset_guarda_redes_v2.csv"):
    """
    Loads and pre-processes the dataset.
    """
    df = pd.read_csv(csv_path)
    if "session_date" in df.columns:
        df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce")
    return df


def validar_dataset(df):
    """
    Ensures the dataset has all required columns for the visualizations.
    """
    colunas_obrigatorias = [
        "session_type", "outcome", "target_y", "target_z",
        "game_minute", "shooter_role"
    ]
    if df.empty or not all(c in df.columns for c in colunas_obrigatorias):
        st.error("⚠️ Dataset inválido ou com colunas em falta.")
        st.stop()
    return True


def filtrar_dados_jogo(df, modo_analise, oponente_selecionado=None, id_sessao=None):
    """
    Filters data based on the selected analysis mode (Aggregated vs Individual).
    """
    df_games = df[df["session_type"] == "GAME"].copy()
    if modo_analise == "Visão Geral (Agregada)":
        if oponente_selecionado == "Todos os Adversários":
            df_filtrado = df_games.copy()
            titulo = "Performance Global da Época"
        else:
            df_filtrado = df_games[df_games["opponent"] == oponente_selecionado].copy()
            titulo = f"Performance vs {oponente_selecionado}"
    else:
        if id_sessao:
             df_filtrado = df_games[df_games["session_id"] == id_sessao].copy()
             titulo = "Análise de Jogo Individual"
        else:
             df_filtrado = df_games.copy()
             titulo = "Análise de Jogo"
    return df_filtrado, titulo


def calcular_metricas_topo(df_filtrado):
    """
    Calculates top-level metrics: total shots, goals, saves, and efficiency percentage.
    """
    t = len(df_filtrado)
    g = len(df_filtrado[df_filtrado['outcome'] == 'GOAL'])
    d = len(df_filtrado[df_filtrado['outcome'] == 'SAVE'])
    eff = (d / t * 100) if t > 0 else 0
    return t, g, d, eff


def calcular_estatisticas_posicao(df_filtrado, asc_order):
    """
    Calculates efficiency statistics for each shooter role.
    """
    if df_filtrado.empty:
        return pd.DataFrame()
    df_role_stats = df_filtrado.groupby('shooter_role', observed=True).apply(
        lambda x: pd.Series({
            'Total': len(x), 
            'Defesas': len(x[x['outcome'] == 'SAVE']), 
            'Eficacia': (len(x[x['outcome'] == 'SAVE']) / len(x) * 100) if len(x) > 0 else 0
        })
    ).reset_index().sort_values('Eficacia', ascending=asc_order)
    return df_role_stats


def preparar_matriz_temporal(df_filtrado):
    """
    Prepares a time-sequence mapping for game sessions.
    """
    df_temp = df_filtrado.copy()
    game_dates = sorted(df_temp['session_date'].unique())
    date_to_seq = {date: i+1 for i, date in enumerate(game_dates)}
    df_temp['game_seq'] = df_temp['session_date'].map(date_to_seq)
    return df_temp, game_dates


def calcular_estatisticas_tecnicas(df_z3_filtrado):
    """
    Calculates technical stats including efficiency and reaction time per shot type.
    """
    try:
        if len(df_z3_filtrado) > 0 and 'shot_type' in df_z3_filtrado.columns:
            df_type_stats = df_z3_filtrado.groupby('shot_type', observed=True).apply(
                lambda x: pd.Series({
                    'Total': len(x),
                    'Defesas': len(x[x['outcome'] == 'SAVE']),
                    'Eficacia': (len(x[x['outcome'] == 'SAVE']) / len(x) * 100) if len(x) > 0 else 0,
                    'Reacao_Media': x['reaction_time_ms'].mean()
                }), include_groups=False
            ).reset_index()
            return df_type_stats
    except Exception:
        pass
    return pd.DataFrame()


def filtrar_zona_1(df_filtrado, shared_shooter_sel, shared_tempo_sel):
    """
    Applies filters for the Spatial Visualization Zone.
    """
    df_viz = df_filtrado.copy()
    if shared_shooter_sel:
        df_viz = df_viz[df_viz['shooter_role'].isin(shared_shooter_sel)]
    df_viz = df_viz[df_viz['game_minute'].between(shared_tempo_sel[0], shared_tempo_sel[1])]
    return df_viz


def filtrar_zona_2(df_filtrado, sel_tipos, sel_jogos):
    """
    Applies filters for the Temporal Evolution Zone (Matrix).
    """
    df_temp = df_filtrado.copy()
    game_dates = sorted(df_temp['session_date'].unique())
    date_to_seq = {date: i+1 for i, date in enumerate(game_dates)}
    df_temp['game_seq'] = df_temp['session_date'].map(date_to_seq)
    if sel_tipos:
        df_temp = df_temp[df_temp['shot_type'].isin(sel_tipos)]
    df_temp = df_temp[df_temp['game_seq'].between(sel_jogos[0], sel_jogos[1])]
    return df_temp


def filtrar_zona_3(df_filtrado, sel_tipos, sel_roles, sel_minuto):
    """
    Applies filters for the Technical Analysis Zone.
    """
    df_z3 = df_filtrado.copy()
    if sel_tipos:
        df_z3 = df_z3[df_z3['shot_type'].isin(sel_tipos)]
    if sel_roles:
        df_z3 = df_z3[df_z3['shooter_role'].isin(sel_roles)]
    df_z3 = df_z3[df_z3['game_minute'].between(sel_minuto[0], sel_minuto[1])]
    return df_z3


def filtrar_zona_4(df_filtrado, sel_bpm, sel_reaction, sel_roles, sel_tipos, sel_minuto):
    """
    Applies filters for the Biometrics and Performance Zone.
    """
    df_z4 = df_filtrado.copy()
    if sel_bpm:
        df_z4 = df_z4[df_z4['heart_rate'].between(sel_bpm[0], sel_bpm[1])]
    if sel_reaction:
        df_z4 = df_z4[df_z4['reaction_time_ms'].between(sel_reaction[0], sel_reaction[1])]
    if sel_roles:
        df_z4 = df_z4[df_z4['shooter_role'].isin(sel_roles)]
    if sel_tipos:
        df_z4 = df_z4[df_z4['shot_type'].isin(sel_tipos)]
    if sel_minuto:
        df_z4 = df_z4[df_z4['game_minute'].between(sel_minuto[0], sel_minuto[1])]
    return df_z4
