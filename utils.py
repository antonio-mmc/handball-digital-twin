import pandas as pd
import streamlit as st
import numpy as np
from typing import Tuple, List, Optional, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from fpdf import FPDF
import io

# Translation dictionary for Internationalization (i18n)
TRANSLATIONS = {
    "pt": {
        "page_title": "Digital Twin: Guarda-Redes",
        "header_title": "🛡️ Digital Twin: Guarda-Redes Andebol",
        "header_subtitle": "Análise de Performance e Biometria em Tempo Real",
        "nav_spatial": "🥅 Espacial",
        "nav_temporal": "📈 Temporal",
        "nav_technical": "🎯 Técnica",
        "nav_biometric": "🧬 Biometria",
        "analysis_module": "MÓDULO DE ANÁLISE",
        "sidebar_info": "💡 As visualizações sofrem ajustes automáticos consoante o modo selecionado.",
        "level_detail": "Nível de Detalhe:",
        "general_view": "Visão Geral (Agregada)",
        "individual_analysis": "Análise de Jogo Individual",
        "global_filters": "FILTROS GLOBAIS",
        "opponent": "Oponente:",
        "all_opponents": "Todos os Adversários",
        "select_game": "Selecionar Jogo Específico:",
        "dark_mode": "Modo Escuro",
        "light_mode": "Modo Claro",
        "change_theme": "Mudar Tema",
        "no_data": "Sem dados para os filtros selecionados.",
        "metrics_total_shots": "Remates Totais",
        "metrics_saves": "Defesas",
        "metrics_goals": "Golos",
        "metrics_avg_bpm": "BPM Médio",
        "metrics_avg_reaction": "Reação Média",
        "metrics_efficiency": "Eficácia",
        "zone1_title": "🥅 Visualização Espacial",
        "filter_zone1": "FILTROS ZONA 1",
        "shooter_pos": "Posição do Atacante",
        "game_minute": "Minuto de Jogo",
        "points": "Pontos",
        "map_detail": "Detalhe Mapa",
        "opacity": "Opacidade",
        "chart_order": "Ordem Gráfico",
        "ascending": "Crescente",
        "descending": "Decrescente",
        "heatmap_title": "Mapa de Calor da Baliza",
        "no_shots": "Sem remates na baliza.",
        "efficiency_pos": "Eficácia por Posição do Atacante",
        "defense_rate_zone": "📊 Taxa de Defesa por Zona",
        "position_map": "📍 Mapa de Posições",
        "zone2_title": "📈 Evolução da Eficácia Técnica",
        "filter_zone2": "FILTROS ZONA 2",
        "shot_type": "Tipo de Remate",
        "game_range": "Intervalo de Jogos",
        "matrix_title": "📊 Matriz de Eficácia: Jogo vs Tipo de Remate",
        "zone3_title": "🎯 Análise Técnica: Dinâmica do Remate",
        "filter_zone3": "FILTROS ZONA 3",
        "ranking_efficiency": "Ranking de Eficácia (%)",
        "avg_reaction_speed": "Rapidez de Reação Média (ms)",
        "zone4_title": "🧬 Biometria e Performance Humana",
        "filter_zone4": "FILTROS ZONA 4",
        "general_filters": "Filtros Gerais",
        "bpm": "BPM",
        "outcome": "Resultado",
        "show_lines": "Mostrar Linhas",
        "correlation_title": "Correlação: Cansaço vs Tempo de Reação",
        "temporal_evolution": "Evolução Temporal no Jogo",
        "raw_data_expand": "📂 Explorar Dados Brutos (Data Log)",
        "predictive_twin": "🧠 Inteligência Preditiva (ML)",
        "prediction_probability": "Probabilidade de Defesa",
        "export_report": "📥 Exportar Relatório PDF",
        "save_model_help": "Modelo treinado para prever a probabilidade de defesa baseado em 1400+ eventos históricos.",
        "reaction_help": "Tempo entre a saída da bola e o início do movimento de defesa.",
        "bpm_help": "Frequência cardíaca captada via sensores biométricos em tempo real.",
        "stats_all_season": "Performance Global da Época",
        "stats_vs": "Performance vs",
        "stats_game_analysis": "Análise de Jogo Individual",
        "analysis_of": "Análise do Jogo:",
        "nav_predictive": "🧠 Previsão",
        "zone5_title": "🧠 Inteligência Preditiva",
        "filter_zone5": "FILTROS ZONA 5",
        "all_f": "Todas",
        "all_m": "Todos",
        "technique": "Técnica",
        "velocity": "Velocidade",
        "tech_basic": "Base",
        "tech_block": "Bloco",
        "tech_kick": "Pontapé",
        "tech_split": "Espargata",
        "tech_star": "Estrela",
        "glossary_title": "📖 Guia de Técnicas",
        "glossary_basic": "**Base**: Posição neutra de prontidão.",
        "glossary_block": "**Bloco**: Uso do tronco e braços para fechar o ângulo.",
        "glossary_kick": "**Pontapé**: Defesa rápida com a perna nos cantos inferiores.",
        "glossary_split": "**Espargata**: Abertura total de pernas para cobrir a base.",
        "glossary_star": "**Estrela**: Extensão total de membros para ocupação máxima."
    },
    "en": {
        "page_title": "Digital Twin: Goalkeeper",
        "header_title": "🛡️ Handball Goalkeeper Digital Twin",
        "header_subtitle": "Real-Time Performance & Biometric Analysis",
        "nav_spatial": "🥅 Spatial",
        "nav_temporal": "📈 Temporal",
        "nav_technical": "🎯 Technical",
        "nav_biometric": "🧬 Biometric",
        "analysis_module": "ANALYSIS MODULE",
        "sidebar_info": "💡 Visualizations automatically adjust based on the selected mode.",
        "level_detail": "Level of Detail:",
        "general_view": "General view (Aggregated)",
        "individual_analysis": "Individual Game Analysis",
        "global_filters": "GLOBAL FILTERS",
        "opponent": "Opponent:",
        "all_opponents": "All Opponents",
        "select_game": "Select Specific Game:",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "change_theme": "Change Theme",
        "no_data": "No data for the selected filters.",
        "metrics_total_shots": "Total Shots",
        "metrics_saves": "Saves",
        "metrics_goals": "Goals",
        "metrics_avg_bpm": "Avg BPM",
        "metrics_avg_reaction": "Avg Reaction",
        "metrics_efficiency": "Efficiency",
        "zone1_title": "🥅 Spatial Visualization",
        "filter_zone1": "ZONE 1 FILTERS",
        "shooter_pos": "Shooter Position",
        "game_minute": "Game Minute",
        "points": "Points",
        "map_detail": "Map Detail",
        "opacity": "Opacity",
        "chart_order": "Chart Order",
        "ascending": "Ascending",
        "descending": "Descending",
        "heatmap_title": "Goal Heatmap",
        "no_shots": "No shots on goal.",
        "efficiency_pos": "Efficiency by Shooter Position",
        "defense_rate_zone": "📊 Defense Rate by Zone",
        "position_map": "📍 Position Map",
        "zone2_title": "📈 Technical Efficiency Evolution",
        "filter_zone2": "ZONE 2 FILTERS",
        "shot_type": "Shot Type",
        "game_range": "Game Range",
        "matrix_title": "📊 Efficiency Matrix: Game vs Shot Type",
        "zone3_title": "🎯 Technical Analysis: Shot Dynamics",
        "filter_zone3": "ZONE 3 FILTERS",
        "ranking_efficiency": "Efficiency Ranking (%)",
        "avg_reaction_speed": "Avg Reaction Speed (ms)",
        "zone4_title": "🧬 Biometrics & Human Performance",
        "filter_zone4": "ZONE 4 FILTERS",
        "general_filters": "General Filters",
        "bpm": "BPM",
        "outcome": "Outcome",
        "show_lines": "Show Lines",
        "correlation_title": "Correlation: Fatigue vs Reaction Time",
        "temporal_evolution": "Temporal Evolution in Game",
        "raw_data_expand": "📂 Explore Raw Data (Data Log)",
        "predictive_twin": "🧠 Predictive Intelligence (ML)",
        "prediction_probability": "Save Probability",
        "export_report": "📥 Export PDF Report",
        "save_model_help": "Model trained to predict save probability based on 1400+ historical events.",
        "reaction_help": "Time between ball release and start of defense movement.",
        "bpm_help": "Heart rate captured via biometric sensors in real time.",
        "stats_all_season": "Global Season Performance",
        "stats_vs": "Performance vs",
        "stats_game_analysis": "Individual Game Analysis",
        "analysis_of": "Game Analysis:",
        "nav_predictive": "🧠 Prediction",
        "zone5_title": "🧠 Predictive Intelligence",
        "filter_zone5": "FILTERS ZONE 5",
        "all_f": "All",
        "all_m": "All",
        "technique": "Technique",
        "velocity": "Velocity",
        "tech_basic": "Basic",
        "tech_block": "Block",
        "tech_kick": "Kick",
        "tech_split": "Split",
        "tech_star": "Star",
        "glossary_title": "📖 Technique Guide",
        "glossary_basic": "**Basic**: Standard ready position.",
        "glossary_block": "**Block**: Using torso and arms to close the angle.",
        "glossary_kick": "**Kick**: Quick leg save for low corners.",
        "glossary_split": "**Split**: Full leg extension to cover the base.",
        "glossary_star": "**Star**: Full limb extension for maximum coverage."
    }
}

def tr(key: str, lang: str = "pt") -> str:
    """
    Returns the translated string for a given key and language.
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["pt"]).get(key, key)

def mapear_tecnica(tech_code: str, lang: str = "pt") -> str:
    """
    Maps raw technique codes (BASIC, STAR, etc.) to professional translated names.
    """
    mapping = {
        "BASIC": "tech_basic",
        "BLOCK": "tech_block",
        "KICK": "tech_kick",
        "SPLIT": "tech_split",
        "STAR": "tech_star"
    }
    key = mapping.get(tech_code, tech_code)
    return tr(key, lang)

def obter_glossario_tecnico(lang: str = "pt") -> str:
    """
    Returns a markdown-formatted glossary of goalkeeper techniques.
    """
    items = ["basic", "block", "kick", "split", "star"]
    glossary = ""
    for item in items:
        glossary += f"- {tr('glossary_' + item, lang)}\n"
    return glossary

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


def validar_dataset(df: pd.DataFrame) -> bool:
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


def filtrar_dados_jogo(df: pd.DataFrame, modo_analise: str, lang: str = "pt", oponente_selecionado: str = None, id_sessao: str = None) -> Tuple[pd.DataFrame, str]:
    """
    Filters data based on the selected analysis mode (Aggregated vs Individual).
    """
    df_games = df[df["session_type"] == "GAME"].copy()
    if modo_analise == tr("general_view", lang):
        if oponente_selecionado == tr("all_opponents", lang):
            df_filtrado = df_games.copy()
            titulo = tr("stats_all_season", lang)
        else:
            df_filtrado = df_games[df_games["opponent"] == oponente_selecionado].copy()
            titulo = f"{tr('stats_vs', lang)} {oponente_selecionado}"
    else:
        if id_sessao:
             df_filtrado = df_games[df_games["session_id"] == id_sessao].copy()
             titulo = tr("stats_game_analysis", lang)
        else:
             df_filtrado = df_games.copy()
             titulo = tr("stats_game_analysis", lang)
    return df_filtrado, titulo


def calcular_metricas_topo(df_filtrado: pd.DataFrame) -> Tuple[int, int, int, float]:
    """
    Calculates top-level metrics: total shots, goals, saves, and efficiency percentage.
    """
    t = len(df_filtrado)
    g = len(df_filtrado[df_filtrado['outcome'] == 'GOAL'])
    d = len(df_filtrado[df_filtrado['outcome'] == 'SAVE'])
    eff = (d / t * 100) if t > 0 else 0
    return t, g, d, eff


def calcular_estatisticas_posicao(df_filtrado: pd.DataFrame, asc_order: bool) -> pd.DataFrame:
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
        }), include_groups=False
    ).reset_index().sort_values('Eficacia', ascending=asc_order)
    return df_role_stats


def preparar_matriz_temporal(df_filtrado: pd.DataFrame) -> Tuple[pd.DataFrame, List[pd.Timestamp]]:
    """
    Prepares a time-sequence mapping for game sessions.
    """
    df_temp = df_filtrado.copy()
    game_dates = sorted(df_temp['session_date'].unique())
    date_to_seq = {date: i+1 for i, date in enumerate(game_dates)}
    df_temp['game_seq'] = df_temp['session_date'].map(date_to_seq)
    return df_temp, game_dates


def calcular_estatisticas_tecnicas(df_z3_filtrado: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates technical stats including efficiency and reaction time per shot type.
    """
    try:
        if not df_z3_filtrado.empty and 'shot_type' in df_z3_filtrado.columns:
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


def filtrar_zona_1(df_filtrado: pd.DataFrame, shared_shooter_sel: List[str], shared_tempo_sel: Tuple[int, int]) -> pd.DataFrame:
    """
    Applies filters for the Spatial Visualization Zone.
    """
    df_viz = df_filtrado.copy()
    if shared_shooter_sel:
        df_viz = df_viz[df_viz['shooter_role'].isin(shared_shooter_sel)]
    df_viz = df_viz[df_viz['game_minute'].between(shared_tempo_sel[0], shared_tempo_sel[1])]
    return df_viz


def filtrar_zona_2(df_filtrado: pd.DataFrame, sel_tipos: List[str], sel_jogos: Tuple[int, int]) -> pd.DataFrame:
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


def filtrar_zona_3(df_filtrado: pd.DataFrame, sel_tipos: List[str], sel_roles: List[str], sel_minuto: Tuple[int, int]) -> pd.DataFrame:
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


def filtrar_zona_4(df_filtrado: pd.DataFrame, sel_bpm: Tuple[int, int], sel_reaction: Tuple[int, int], sel_roles: List[str], sel_tipos: List[str], sel_minuto: Tuple[int, int]) -> pd.DataFrame:
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

def calcular_correlacao_pearson(df: pd.DataFrame) -> float:
    # Function deprecated as requested.
    return 0.0

@st.cache_resource
def treinar_modelo(df: pd.DataFrame) -> Tuple[Optional[RandomForestClassifier], dict]:
    """
    Trains a Random Forest model to predict the probability of a save.
    Returns the model and the label encoders.
    """
    try:
        # Filter for on-target shots only (SAVE or GOAL)
        df_ml = df[df['outcome'].isin(['SAVE', 'GOAL'])].copy()
        
        # Features and Target
        features = ['shooter_role', 'shot_type', 'technique', 'velocity_kmh', 'target_y', 'target_z', 'heart_rate']
        target = 'outcome'
        
        df_ml = df_ml.dropna(subset=features + [target])
        
        if df_ml.empty:
            return None, {}
            
        # Encode categorical variables
        encoders = {}
        for col in ['shooter_role', 'shot_type', 'technique']:
            le = LabelEncoder()
            df_ml[col] = le.fit_transform(df_ml[col].astype(str))
            encoders[col] = le
            
        X = df_ml[features]
        y = (df_ml[target] == 'SAVE').astype(int)
        
        model = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_leaf=4, random_state=42)
        model.fit(X, y)
        
        return model, encoders
    except Exception as e:
        st.error(f"Error training model: {e}")
        return None, {}

def prever_probabilidade(model: RandomForestClassifier, encoders: dict, features_dict: dict) -> float:
    """
    Predicts the probability of a save using the trained model.
    Enforces the exact column order used during training.
    """
    if not model:
        return 0.0
    try:
        # Define the exact feature list used during training
        feature_list = ['shooter_role', 'shot_type', 'technique', 'velocity_kmh', 'target_y', 'target_z', 'heart_rate']
        
        # Prepare input data with the correct order
        input_data = pd.DataFrame([features_dict])
        
        # Add missing features if any (defensive)
        for f in feature_list:
            if f not in input_data.columns:
                input_data[f] = 0.0
        
        # Reorder columns to match training
        input_data = input_data[feature_list]
        
        # Encode categorical variables
        for col, le in encoders.items():
            if col in input_data.columns:
                obs = str(input_data[col].iloc[0])
                if obs in le.classes_:
                    input_data[col] = le.transform([obs])[0]
                else:
                    input_data[col] = 0 
        
        # Predict probability for class 1 (SAVE)
        prob = model.predict_proba(input_data)[0][1]
        
        return float(prob)
    except Exception:
        return 0.0

def _fig_to_img(fig, w_px: int, h_px: int):
    """
    Converts a Plotly figure to a high-res PNG BytesIO stream.
    Forces automargin on axes and generous fixed margins so labels are never cropped.
    """
    import io
    # Activate automargin on both axes (plotly will expand margins if labels don't fit)
    try:
        fig.update_xaxes(automargin=True)
        fig.update_yaxes(automargin=True)
    except Exception:
        pass
    # Set larger fixed margins as a base (automargin adds on top)
    fig.update_layout(
        margin=dict(l=110, r=80, t=60, b=90, autoexpand=True)
    )
    img_bytes = fig.to_image(format="png", width=w_px, height=h_px, scale=1)
    buf = io.BytesIO(img_bytes)
    buf.name = "chart.png"
    return buf


def gerar_pdf_resumo(df: pd.DataFrame, lang: str, titulo: str, active_filters: list,
                     metrics: dict, figure_rows: list = None) -> bytes:
    """
    Generates a professional PDF report mirroring the Streamlit dashboard layout.
    Zones 1-4 only (no predictive / raw data).
    """
    import io

    # ── helpers ─────────────────────────────────────────────────────────────
    def clean(t: str) -> str:
        return ''.join(c for c in str(t) if ord(c) <= 255).strip()

    # Metric colour map (R,G,B)
    METRIC_COLORS = {
        0: (33, 33, 33),    # Total shots  – black
        1: (46, 125, 50),   # Saves        – green
        2: (198, 40, 40),   # Goals        – red
        3: (230, 81, 0),    # Avg BPM      – orange
        4: (21, 101, 192),  # Avg Reaction – blue
    }

    PAGE_W = 210            # A4 width mm
    PAGE_H = 297            # A4 height mm
    MARGIN = 12             # side margins mm
    BODY_W = PAGE_W - 2 * MARGIN   # 186 mm

    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── HEADER (solid dark background via filled cell) ─────────────────────
    HDR_H = 28  # header height mm
    pdf.set_fill_color(30, 33, 41)      # #1e2129
    pdf.set_font("helvetica", "B", 17)  # must set font before any cell() call
    pdf.set_xy(0, 0)
    pdf.cell(PAGE_W, HDR_H, "", fill=True, ln=True)   # full-width filled cell

    # Title (white, bold)
    pdf.set_xy(MARGIN, 5)
    pdf.set_font("helvetica", "B", 17)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(BODY_W, 9, clean(tr("header_title", lang)), align="L")

    # Subtitle (light blue)
    pdf.set_xy(MARGIN, 16)
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(160, 210, 240)
    pdf.cell(BODY_W, 7, clean(tr("header_subtitle", lang)), align="L")

    # Move cursor below header
    pdf.set_xy(MARGIN, HDR_H + 4)
    pdf.set_text_color(0, 0, 0)

    # ── CONTEXT / ANALYSIS TITLE ────────────────────────────────────────────
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(50, 90, 150)
    pdf.cell(BODY_W, 6, clean(titulo), ln=True, align="L")
    pdf.ln(1)

    # Active filters line
    pdf.set_font("helvetica", "", 8)
    pdf.set_text_color(110, 110, 110)
    ctx = "  |  ".join([clean(f) for f in active_filters])
    pdf.multi_cell(BODY_W, 5, ctx, align="L")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # ── TOP METRICS ──────────────────────────────────────────────────────────
    metric_items = list(metrics.items())
    col_w = BODY_W / max(len(metric_items), 1)

    # Background band for metrics
    y_met = pdf.get_y()
    pdf.set_fill_color(245, 247, 250)
    pdf.set_xy(MARGIN, y_met)
    pdf.cell(BODY_W, 20, "", fill=True)

    # Labels row
    pdf.set_xy(MARGIN, y_met + 2)
    pdf.set_font("helvetica", "", 7)
    pdf.set_text_color(120, 120, 120)
    for label, _ in metric_items:
        pdf.cell(col_w, 5, clean(label), align="C")
    pdf.ln(5)

    # Values row with colour
    pdf.set_font("helvetica", "B", 14)
    for idx, (_, value) in enumerate(metric_items):
        r, g, b = METRIC_COLORS.get(idx, (0, 0, 0))
        pdf.set_text_color(r, g, b)
        pdf.cell(col_w, 10, str(value), align="C")
    pdf.ln(12)

    # Main horizontal rule
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(190, 190, 190)
    pdf.set_line_width(0.4)
    pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
    pdf.ln(4)

    if not figure_rows:
        return bytes(pdf.output())

    # ── CHART LAYOUT CONSTANTS ───────────────────────────────────────────────
    GAP        = 4          # gap between side-by-side charts mm
    IMG_W_HALF = (BODY_W - GAP) / 2    # ~91mm each
    IMG_W_FULL = BODY_W                 # ~186mm
    IMG_H_HALF = 80         # mm – taller = more space for labels
    IMG_H_FULL = 100        # mm

    # Pixels to render at (high-res to avoid pixelation when printed)
    REND_W_HALF = 1400      # px – half-width charts
    REND_H_HALF = 900       # px
    REND_W_FULL = 1800      # px – full-width charts
    REND_H_FULL = 900       # px

    def draw_section_title(title_text: str):
        """Zone section header with coloured bar — mirrors app zone headers."""
        y_cur = pdf.get_y()
        # Coloured left accent bar
        pdf.set_fill_color(30, 33, 41)
        pdf.rect(MARGIN, y_cur, 3, 7, style="F")
        # Title text
        pdf.set_xy(MARGIN + 5, y_cur)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(30, 33, 41)
        pdf.cell(BODY_W - 5, 7, clean(title_text), ln=True, align="L")
        # Underline
        pdf.set_draw_color(100, 140, 200)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
        pdf.set_line_width(0.2)
        pdf.set_draw_color(190, 190, 190)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

    def draw_chart_subtitle(title_text: str, x: float, w: float, y: float):
        """Small grey subtitle centred over a chart."""
        pdf.set_xy(x, y)
        pdf.set_font("helvetica", "I", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(w, 4, clean(title_text), align="C")
        pdf.set_text_color(0, 0, 0)

    def place_image_at(fig, x_mm, y_mm, w_mm, h_mm, w_px, h_px):
        """Render fig to PNG and embed in PDF at exact position."""
        try:
            buf = _fig_to_img(fig, w_px, h_px)
            pdf.image(buf, x=x_mm, y=y_mm, w=w_mm, h=h_mm)
        except Exception:
            pass

    # ── RENDER EACH ROW ──────────────────────────────────────────────────────
    for row in figure_rows:
        if not row:
            continue

        # Zone section title
        zt = row[0].get('zone_title', '') if isinstance(row[0], dict) else ''
        if zt:
            if pdf.get_y() > 230:
                pdf.add_page()
            else:
                pdf.ln(3)
            draw_section_title(zt)

        num_cols = len(row)
        is_full  = (num_cols == 1 or row[0].get('full_width', False))

        img_w = IMG_W_FULL if is_full else IMG_W_HALF
        img_h = IMG_H_FULL if is_full else IMG_H_HALF
        rend_w = REND_W_FULL if is_full else REND_W_HALF
        rend_h = REND_H_FULL if is_full else REND_H_HALF

        # Space check: need title(4) + img + gap(5)
        needed = 4 + img_h + 5
        if pdf.get_y() + needed > PAGE_H - 15:
            pdf.add_page()

        # Chart subtitles (small italic above each chart)
        y_title_row = pdf.get_y()
        if is_full:
            draw_chart_subtitle(row[0].get('title', ''), MARGIN, img_w, y_title_row)
            pdf.ln(5)
        else:
            x0 = MARGIN
            x1 = MARGIN + img_w + GAP
            draw_chart_subtitle(row[0].get('title', ''), x0, img_w, y_title_row)
            if len(row) > 1:
                draw_chart_subtitle(row[1].get('title', ''), x1, img_w, y_title_row)
            pdf.ln(5)

        y_img = pdf.get_y()

        # Render and place images
        if is_full:
            place_image_at(row[0].get('fig'), MARGIN, y_img, img_w, img_h, rend_w, rend_h)
        else:
            x0 = MARGIN
            x1 = MARGIN + img_w + GAP
            place_image_at(row[0].get('fig'), x0, y_img, img_w, img_h, rend_w, rend_h)
            if len(row) > 1:
                place_image_at(row[1].get('fig'), x1, y_img, img_w, img_h, rend_w, rend_h)

        # Advance cursor below images
        pdf.set_y(y_img + img_h + 5)

    return bytes(pdf.output())


