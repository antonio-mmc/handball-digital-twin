"""
Main Application for the Digital Twin Goalkeeper Dashboard.
Built with Streamlit and Plotly.
"""
# LIBRARIES
import streamlit as st
import utils
import charts


# PAGE CONFIGURATION
st.set_page_config(
    page_title="Digital Twin: Guarda-Redes",
    layout="wide",
    page_icon="🧤",
    initial_sidebar_state="expanded"
)


# Load CSS and Data
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

theme_key = "dark" if st.session_state.dark_mode else "light"
theme_colors = utils.THEMES[theme_key]

utils.carregar_css(theme_key)
df = utils.carregar_dados()
utils.validar_dataset(df)


# Filter for games only
df_games = df[df["session_type"] == "GAME"].copy()

# SIDEBAR CONFIGURATION
with st.sidebar:
    # NAVIGATION MENU
    st.markdown("""
    <div class="nav-container-sidebar" style="margin-bottom: 20px;">
        <a href="#zone1" class="nav-link-sidebar">🥅 Espacial</a>
        <a href="#zone2" class="nav-link-sidebar">📈 Temporal</a>
        <a href="#zone3" class="nav-link-sidebar">🎯 Técnica</a>
        <a href="#zone4" class="nav-link-sidebar">🧬 Biometria</a>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("<p class='sidebar-section-title'>ANALYSIS MODULE</p>", unsafe_allow_html=True)
    modo_analise = st.radio(
        "Level of Detail:",
        ("Visão Geral (Agregada)", "Análise de Jogo Individual"),
        index=0,
        label_visibility="collapsed"
    )


    st.markdown("<p class='sidebar-section-title'>GLOBAL FILTERS</p>", unsafe_allow_html=True)

    is_aggregated_view = (modo_analise == "Visão Geral (Agregada)")

    if is_aggregated_view:
        oponentes = ["Todos os Adversários"] + sorted(df_games["opponent"].dropna().unique().tolist())
        escolha_oponente = st.selectbox("Oponente:", oponentes, label_visibility="collapsed")
        df_filtrado, titulo_contexto = utils.filtrar_dados_jogo(df, modo_analise, oponente_selecionado=escolha_oponente)
    else:
        lista_jogos = (
            df_games.loc[df_games["session_date"].notna(), ["session_id", "session_date", "opponent"]]
            .drop_duplicates()
            .sort_values("session_date", ascending=False)
        )
        lista_jogos["label"] = lista_jogos["session_date"].dt.strftime("%d/%m/%Y") + " vs " + lista_jogos["opponent"]

        escolha_label = st.selectbox("Selecionar Jogo Específico:", lista_jogos["label"])
        id_sessao = lista_jogos.loc[lista_jogos["label"] == escolha_label, "session_id"].iloc[0]

        df_filtrado, _ = utils.filtrar_dados_jogo(df, modo_analise, id_sessao=id_sessao)
        titulo_contexto = f"Análise do Jogo: {escolha_label}"

    st.markdown("<hr style='margin-top: -10px; margin-bottom: 20px; border: 0; border-top: 1px solid rgba(255, 255, 255, 0.2);'>", unsafe_allow_html=True)
    st.info("💡 As visualizações sofrem ajustes automáticos consoante o modo selecionado.")

    label_tema = "Modo Escuro" if st.session_state.dark_mode else "Modo Claro"
    st.markdown(f"<p class='sidebar-section-title' style='margin-top: 15px;'>{label_tema}</p>", unsafe_allow_html=True)
    c_theme1, c_theme2 = st.columns([2, 5])
    with c_theme1:
        st.markdown(f"<p style='font-size: 1.5rem; margin-top: -5px;'>{'🌙' if st.session_state.dark_mode else '☀️'}</p>", unsafe_allow_html=True)
    with c_theme2:
        st.toggle("Mudar Tema", key="dark_mode", label_visibility="collapsed")

if df_filtrado.empty:
    st.warning("Sem dados para os filtros selecionados.")
    st.stop()


# MAIN HEADER 
st.markdown(f"""<div class="main-header-container">
    <h1 class="main-header-title">🛡️ Digital Twin: Guarda-Redes Andebol</h1>
    <h3 class="main-header-subtitle">Análise de Performance e Biometria em Tempo Real</h3>
</div>""", unsafe_allow_html=True)
st.divider()


# TOP METRICS DASHBOARD
t, g, d, eff = utils.calcular_metricas_topo(df_filtrado)

st.markdown(f"""
<div class="metrics-container">
    <div class="metric-box">
        <div class="metric-label">Remates Totais</div>
        <div class="metric-value metric-black">{t}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">Defesas</div>
        <div class="metric-value metric-green">{d}</div>
        <div class="metric-badge">{eff:.1f}% Eficácia</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">Golos</div>
        <div class="metric-value metric-red">{g}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">BPM Médio</div>
        <div class="metric-value metric-orange">{df_filtrado['heart_rate'].mean():.0f} <span class="metric-unit">bpm</span></div>
    </div>
    <div class="metric-box">
        <div class="metric-label">Reação Média</div>
        <div class="metric-value metric-blue">{df_filtrado['reaction_time_ms'].mean():.0f} <span class="metric-unit">ms</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ZONA 1
st.markdown(f"<div id='zone1'></div><h3 class='zone-header-title'>🥅 Visualização Espacial: {titulo_contexto}</h3>", unsafe_allow_html=True)

# FILTROS ZONA 1 - LINHA 1
c1_r1_c1, c1_r1_c2, c1_r1_c3, c1_r1_c4, c1_r1_c5 = st.columns([1.0, 0.1, 2.0, 2.0, 0.5])
with c1_r1_c1:
    st.markdown("<span class='f-row-top filter-row-header'>FILTROS<br>ZONA 1</span>", unsafe_allow_html=True)
with c1_r1_c2:
    st.write("")
with c1_r1_c3:
    st.markdown("<p class='filter-label-margin-5'>Posição do Atacante</p>", unsafe_allow_html=True)
    roles = sorted(df_filtrado['shooter_role'].unique().tolist())
    shared_shooter_sel = st.multiselect("Quem?", roles, placeholder="Todas", label_visibility="collapsed")
with c1_r1_c4:
    st.markdown("<p class='filter-label-margin-5'>Minuto de Jogo</p>", unsafe_allow_html=True)
    shared_tempo_sel = st.slider("Minuto:", 0, 60, (0, 60), label_visibility="collapsed")
with c1_r1_c5: 
     st.write("")


# ZONE 1 FILTERS - ROW 2 (Spatial Detail)
c1_r2_c1, c1_r2_c2, c1_r2_c3, c1_r2_c4, c1_r2_c5, c1_r2_c6, c1_r2_c7 = st.columns([0.3, 0.6, 1.1, 1.1, 2.2, 1.0, 1])
with c1_r2_c1:
      st.markdown("<span class='f-row-bottom'></span>", unsafe_allow_html=True)
with c1_r2_c2:
    st.markdown("<p class='filter-label-margin-5'>Pontos</p>", unsafe_allow_html=True)
    mostrar_bolas_local = st.toggle("Pontos", value=True, label_visibility="collapsed")
with c1_r2_c3:
    st.markdown("<p class='filter-label-margin-5'>Detalhe Mapa</p>", unsafe_allow_html=True)
    n_detalhe = st.slider("Detalhe", 5, 40, 20, label_visibility="collapsed")
with c1_r2_c4:
    st.markdown("<p class='filter-label-margin-5'>Opacidade</p>", unsafe_allow_html=True)
    n_opacidade = st.slider("Opacidade", 0.1, 1.0, 0.6, label_visibility="collapsed")
with c1_r2_c5:
    st.write("") 
with c1_r2_c6:
    st.markdown("<p class='filter-label-margin-5'>Ordem Gráfico</p>", unsafe_allow_html=True)
    ordem_sel = st.selectbox("Ordem:", ["Crescente", "Decrescente"], index=0, label_visibility="collapsed")
    asc_order = (ordem_sel == "Crescente")
with c1_r2_c7:
    st.write("")


# FILTERING LOGIC
df_viz_filtrado = utils.filtrar_zona_1(df_filtrado, shared_shooter_sel, shared_tempo_sel)

# ZONE 1 CHARTS (Spatial)
col1, col2 = st.columns(2)
with col1:
    st.markdown("<div class='subtitulo-visualizacao'>Mapa de Calor da Baliza</div>", unsafe_allow_html=True)
    df_golos = df_viz_filtrado[df_viz_filtrado['outcome'] == 'GOAL'].copy()
    if not df_golos.empty:
        st.plotly_chart(charts.gerar_figura_baliza(df_golos, n_detalhe, n_opacidade, mostrar_bolas_local, "assets/baliza.png", theme_colors), use_container_width=True, config={'displayModeBar': False})
        c_grid_l, c_grid_c, c_grid_r = st.columns([0.1, 5.8, 0.1])
        with c_grid_c:
            with st.popover("📊 Taxa de Defesa por Zona", use_container_width=True):
                st.plotly_chart(charts.gerar_grelha_3x3(df_viz_filtrado, theme_colors), use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Sem remates na baliza.")

with col2:
    st.markdown("<div class='subtitulo-visualizacao'>Eficácia por Posição do Atacante</div>", unsafe_allow_html=True)
    df_role_stats = utils.calcular_estatisticas_posicao(df_viz_filtrado, asc_order)
    if not df_role_stats.empty:
        st.plotly_chart(charts.gerar_barras_posicao(df_role_stats, asc_order, theme_colors), use_container_width=True, config={'displayModeBar': False})
        _, c2_pop = st.columns([3, 2])
        with c2_pop:
            with st.popover("📍 Mapa de Posições", use_container_width=True):
                st.image("assets/positions.png", use_container_width=True)
    else:
        st.info("Sem dados para as posições selecionadas.")

st.markdown("---")

# ZONA 2
if is_aggregated_view:
    st.markdown("<div id='zone2'></div><h3 class='zone-header-title-no-margin'>📈 Evolução da Eficácia Técnica</h3>", unsafe_allow_html=True)
    st.write("")
    df_temp, game_dates = utils.preparar_matriz_temporal(df_filtrado)

    # FILTROS ZONA 2
    c2_r1_c1, c2_r1_c2, c2_r1_c3, c2_r1_c4, c2_r1_c5, c2_r1_c6 = st.columns([1.2, 0.5, 2.0, 1.8, 1.6, 0.5])
    with c2_r1_c1:
        st.markdown("<span class='f-row-single filter-row-header'>FILTROS<br>ZONA 2</span>", unsafe_allow_html=True)
    with c2_r1_c2:
        st.write("")
    with c2_r1_c3:
        st.markdown("<p class='filter-label-margin-5'>Tipo de Remate</p>", unsafe_allow_html=True)
        tipos_disponiveis = sorted(df_temp['shot_type'].unique().tolist())
        sel_tipos = st.multiselect("Tipo:", tipos_disponiveis, placeholder="Todos", label_visibility="collapsed", key="z2_tipos")
    with c2_r1_c4:
        st.markdown("<p class='filter-label-margin-5'>Intervalo de Jogos</p>", unsafe_allow_html=True)
        max_jogos = len(game_dates)
        sel_jogos = st.slider("Jogos:", 1, max_jogos, (1, max_jogos), label_visibility="collapsed", key="z2_jogos")
    with c2_r1_c5:
        st.markdown("<p class='filter-label-margin-5'>% Eficácia</p>", unsafe_allow_html=True)
        sel_eficacia = st.slider("Eficácia:", 0, 100, (0, 100), label_visibility="collapsed", key="z2_eficacia")
    with c2_r1_c6:
        st.write("")
    
    df_temp = utils.filtrar_zona_2(df_filtrado, sel_tipos, sel_jogos)
    st.markdown("<div class='subtitulo-visualizacao'>📊 Matriz de Eficácia: Jogo vs Tipo de Remate</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.gerar_matriz_eficacia(df_temp, sel_eficacia, theme_colors), use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

# ZONA 3
st.markdown("<div id='zone3'></div><h3 class='zone-header-title'>🎯 Análise Técnica: Dinâmica do Remate</h3>", unsafe_allow_html=True)
st.write("")

# FILTROS ZONA 3 - LINHA 1
c3_r1_c1, c3_r1_c2, c3_r1_c3, c3_r1_c4, c3_r1_c5, c3_r1_c6 = st.columns([1.0, 0.1, 2.0, 1.5, 1.5, 0.1])
with c3_r1_c1:
    st.markdown("<span class='f-row-top filter-row-header'>FILTROS<br>ZONA 3</span>", unsafe_allow_html=True)
with c3_r1_c2: st.write("")
with c3_r1_c3:
    st.markdown("<p class='filter-label-margin-5'>Tipo de Remate</p>", unsafe_allow_html=True)
    tipos_z3 = sorted(df_filtrado['shot_type'].unique().tolist())
    sel_tipos_z3 = st.multiselect("Tipo:", tipos_z3, placeholder="Todos", label_visibility="collapsed", key="z3_tipos")
with c3_r1_c4:
    st.markdown("<p class='filter-label-margin-5'>Posição</p>", unsafe_allow_html=True)
    roles_z3 = sorted(df_filtrado['shooter_role'].unique().tolist())
    sel_roles_z3 = st.multiselect("Posição:", roles_z3, placeholder="Todas", label_visibility="collapsed", key="z3_roles")
with c3_r1_c5:
    st.markdown("<p class='filter-label-margin-5'>Minuto</p>", unsafe_allow_html=True)
    sel_minuto_z3 = st.slider("Minuto:", 0, 60, (0, 60), label_visibility="collapsed", key="z3_minuto")
with c3_r1_c6: st.write("")

# FILTROS ZONA 3 - LINHA 2
c3_r2_c1, c3_r2_c2, c3_r2_c3, c3_r2_c4, c3_r2_c5, c3_r2_c6, c3_r2_c7 = st.columns([0.1, 0.3, 2.0, 1.0, 2.0, 1.2, 0.5])
with c3_r2_c1:
    st.markdown("<span class='f-row-bottom'></span>", unsafe_allow_html=True)
with c3_r2_c2: st.write("")
with c3_r2_c3:
    st.markdown("<p class='filter-label-margin-5'>% Eficácia</p>", unsafe_allow_html=True)
    sel_efic_range = st.slider("Eficácia:", 0, 100, (0, 100), label_visibility="collapsed", key="z3_efic_range")
with c3_r2_c4: st.write("")
with c3_r2_c5:
    st.markdown("<p class='filter-label-margin-5'>Reação (ms)</p>", unsafe_allow_html=True)
    sel_reacao_range = st.slider("Reação:", 200, 500, (200, 500), label_visibility="collapsed", key="z3_reacao_range")
with c3_r2_c6:
    st.markdown("<p class='filter-label-margin-5'>Ordem</p>", unsafe_allow_html=True)
    ordem_z3 = st.selectbox("Ordem:", ["Crescente", "Decrescente"], index=1, label_visibility="collapsed", key="z3_ordem")
with c3_r2_c7: st.write("")

# PROCESSAMENTO ZONA 3
df_z3_filtrado = utils.filtrar_zona_3(df_filtrado, sel_tipos_z3, sel_roles_z3, sel_minuto_z3)
df_type_stats = utils.calcular_estatisticas_tecnicas(df_z3_filtrado)

# GRÁFICOS ZONA 3
col_tec1, col_tec2 = st.columns(2)
with col_tec1:
    st.markdown("<div class='subtitulo-visualizacao'>Ranking de Eficácia (%)</div>", unsafe_allow_html=True)
    if not df_type_stats.empty and len(df_type_stats) > 0:
        try:
            df_eff = df_type_stats[df_type_stats['Eficacia'].between(sel_efic_range[0], sel_efic_range[1])].copy()
            if not df_eff.empty:
                asc_eff = True if ordem_z3 == "Crescente" else False
                df_eff = df_eff.sort_values('Eficacia', ascending=asc_eff)
                st.plotly_chart(charts.gerar_ranking_eficacia(df_eff, ordem_z3, theme_colors), use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Sem dados no intervalo de eficácia selecionado.")
        except Exception:
            st.info("Sem dados suficientes para mostrar o ranking.")
    else:
        st.info("Sem dados suficientes.")

with col_tec2:
    st.markdown("<div class='subtitulo-visualizacao'>Rapidez de Reação Média (ms)</div>", unsafe_allow_html=True)
    if not df_type_stats.empty and len(df_type_stats) > 0:
        try:
            df_react = df_type_stats[df_type_stats['Reacao_Media'].between(sel_reacao_range[0], sel_reacao_range[1])].copy()
            if not df_react.empty:
                asc_react = True if ordem_z3 == "Crescente" else False
                df_react = df_react.sort_values('Reacao_Media', ascending=asc_react)
                st.plotly_chart(charts.gerar_ranking_reacao(df_react, ordem_z3, theme_colors), use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Sem dados no intervalo de tempo de reação selecionado.")
        except Exception:
            st.info("Sem dados suficientes.")
    else:
        st.info("Sem dados suficientes.")

st.markdown("---")

# ZONA 4
st.markdown("<div id='zone4'></div><h3 class='zone-header-title'>🧬 Biometria e Performance Humana</h3>", unsafe_allow_html=True)
st.write("")

# FILTROS ZONA 4 - LINHA 1
c4_r1_c1, c4_r1_c2, c4_r1_c3, c4_r1_c4, c4_r1_c5, c4_r1_c6, c4_r1_c7 = st.columns([1.2, 0.5, 2.8, 1.6, 1.6, 1.0, 0.5])
with c4_r1_c1:
    st.markdown("<span class='f-row-top filter-row-header'>FILTROS<br>ZONA 4</span>", unsafe_allow_html=True)
with c4_r1_c2: st.write("")
with c4_r1_c3:
    st.markdown("<p class='filter-label-margin-5'>Filtros Gerais</p>", unsafe_allow_html=True)
    c4_sub1, c4_sub2 = st.columns(2)
    with c4_sub1:
        roles_z4 = sorted(df_filtrado['shooter_role'].dropna().unique().tolist()) if 'shooter_role' in df_filtrado.columns else []
        sel_role_z4 = st.multiselect("Posição:", roles_z4, placeholder="Posição", label_visibility="collapsed", key="z4_roles")
    with c4_sub2:
        tipos_z4 = sorted(df_filtrado['shot_type'].dropna().unique().tolist()) if 'shot_type' in df_filtrado.columns else []
        sel_tipo_z4 = st.multiselect("Tipo:", tipos_z4, placeholder="Tipo Remate", label_visibility="collapsed", key="z4_tipos")
with c4_r1_c4:
     st.markdown("<p class='filter-label-margin-5'>BPM</p>", unsafe_allow_html=True)
     hr_min = int(df_filtrado['heart_rate'].min()) if 'heart_rate' in df_filtrado.columns and not df_filtrado['heart_rate'].isna().all() else 40
     hr_max = int(df_filtrado['heart_rate'].max()) if 'heart_rate' in df_filtrado.columns and not df_filtrado['heart_rate'].isna().all() else 200
     sel_bpm = st.slider("BPM:", hr_min, hr_max, (hr_min, hr_max), label_visibility="collapsed", key="z4_bpm")
with c4_r1_c5:
    st.markdown("<p class='filter-label-margin-5'>Reação (ms)</p>", unsafe_allow_html=True)
    rt_min = int(df_filtrado['reaction_time_ms'].min()) if 'reaction_time_ms' in df_filtrado.columns and not df_filtrado['reaction_time_ms'].isna().all() else 150
    rt_max = int(df_filtrado['reaction_time_ms'].max()) if 'reaction_time_ms' in df_filtrado.columns and not df_filtrado['reaction_time_ms'].isna().all() else 700
    sel_reaction = st.slider("Reação:", rt_min, rt_max, (rt_min, rt_max), label_visibility="collapsed", key="z4_reaction")
with c4_r1_c6:
    st.markdown("<p class='filter-label-margin-5'>Minuto</p>", unsafe_allow_html=True)
    sel_minuto_z4 = st.slider("Minuto:", 0, 60, (0, 60), label_visibility="collapsed", key="z4_minuto")
with c4_r1_c7: st.write("")

# FILTROS ZONA 4 - LINHA 2
c4_r2_c1, c4_r2_c2, c4_r2_c3, c4_r2_c4, c4_r2_c5, c4_r2_c6 = st.columns([0.1, 0.5, 2.2, 0.5, 2.2, 0.5])
with c4_r2_c1:
    st.markdown("<span class='f-row-bottom'></span>", unsafe_allow_html=True)
with c4_r2_c2: st.write("")
with c4_r2_c3:
    st.markdown("<p class='filter-label-margin-5'>Outcome</p>", unsafe_allow_html=True)
    outcomes = sorted(df_filtrado['outcome'].dropna().unique().tolist()) if 'outcome' in df_filtrado.columns else []
    sel_outcome_z4 = st.multiselect("Outcome:", outcomes, default=outcomes, label_visibility="collapsed", key="z4_outcome")
with c4_r2_c4: st.write("")
with c4_r2_c5:
    st.markdown("<p class='filter-label-margin-5'>Mostrar Linhas</p>", unsafe_allow_html=True)
    c4_tog1, c4_tog2 = st.columns(2)
    with c4_tog1:
        show_bpm_line = st.checkbox("BPM", value=True, key="z4_show_bpm")
    with c4_tog2:
        show_reaction_line = st.checkbox("Reação", value=True, key="z4_show_reaction")
with c4_r2_c6: st.write("")

# PROCESSAMENTO ZONA 4
df_z4_filtrado = utils.filtrar_zona_4(df_filtrado, sel_bpm, sel_reaction, sel_role_z4, sel_tipo_z4, sel_minuto_z4)

# GRÁFICOS ZONA 4
c_fisio1, c_fisio2 = st.columns(2)
with c_fisio1:
    st.markdown("<div class='subtitulo-visualizacao'>Correlação: Cansaço vs Tempo de Reação</div>", unsafe_allow_html=True)
    df_left = df_z4_filtrado.copy()
    if 'outcome' in df_left.columns and sel_outcome_z4:
        df_left = df_left[df_left['outcome'].isin(sel_outcome_z4)]
    if df_left.empty:
        st.info("Sem dados após aplicar os filtros.")
    else:
        st.plotly_chart(charts.gerar_scatter_correlacao(df_left, theme_colors), use_container_width=True, config={'displayModeBar': False})

with c_fisio2:
    st.markdown("<div class='subtitulo-visualizacao'>Evolução Temporal no Jogo</div>", unsafe_allow_html=True)
    df_right = df_z4_filtrado.sort_values('game_minute')
    if df_right.empty:
        st.info("Sem dados.")
    else:
            st.plotly_chart(charts.gerar_evolucao_temporal(df_right, show_bpm_line, show_reaction_line, theme_colors), use_container_width=True, config={'displayModeBar': False})

st.markdown("---")


# FOOTER / DATA LOG
with st.expander("📂 Explore Raw Data (Digital Twin Data Log)"):
    st.dataframe(df_filtrado.sort_values('game_minute')[['game_minute', 'opponent', 'shooter_role', 'shot_type', 'outcome', 'heart_rate', 'reaction_time_ms', 'velocity_kmh']])