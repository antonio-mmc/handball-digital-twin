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


# LANGUAGE SETUP
if 'lang' not in st.session_state:
    st.session_state.lang = "pt"

# Load CSS and Data
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

theme_key = "dark" if st.session_state.dark_mode else "light"
theme_colors = utils.THEMES[theme_key]
lang = st.session_state.lang

utils.carregar_css(theme_key)
df = utils.carregar_dados()
utils.validar_dataset(df)

# ML MODEL TRAINING
model, encoders = utils.treinar_modelo(df)


# Filter for games only
df_games = df[df["session_type"] == "GAME"].copy()

# SIDEBAR CONFIGURATION
with st.sidebar:
    # 1. COMPACT SETTINGS ROW (Language & Theme)
    c_set1, c_set2 = st.columns([1, 1], gap="small")
    with c_set1:
         # LANGUAGE SELECTOR
        lang_options = {"pt": "🇵🇹 PT", "en": "🇬🇧 EN"}
        st.session_state.lang = st.selectbox(
            "Lang", 
            options=list(lang_options.keys()), 
            format_func=lambda x: lang_options[x],
            label_visibility="collapsed"
        )
        lang = st.session_state.lang

    with c_set2:
        # THEME TOGGLE
        label_tema = "☀️" if not st.session_state.dark_mode else "🌙"
        st.toggle(label_tema, key="dark_mode")

    # 2. NAVIGATION MENU (Reduced size)
    st.markdown(f"""
    <div class="nav-container-sidebar" style="margin-top: 5px; margin-bottom: 10px;">
        <a href="#zone1" class="nav-link-sidebar" style="padding: 6px; font-size: 0.85rem;">{utils.tr('nav_spatial', lang)}</a>
        <a href="#zone2" class="nav-link-sidebar" style="padding: 6px; font-size: 0.85rem;">{utils.tr('nav_temporal', lang)}</a>
        <a href="#zone3" class="nav-link-sidebar" style="padding: 6px; font-size: 0.85rem;">{utils.tr('nav_technical', lang)}</a>
        <a href="#zone4" class="nav-link-sidebar" style="padding: 6px; font-size: 0.85rem;">{utils.tr('nav_biometric', lang)}</a>
        <a href="#zone5" class="nav-link-sidebar" style="padding: 6px; font-size: 0.85rem;">{utils.tr('nav_predictive', lang)}</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<p class='sidebar-section-title' style='font-size: 0.8rem; margin-top:5px;'>{utils.tr('analysis_module', lang)}</p>", unsafe_allow_html=True)
    modo_analise = st.radio(
        utils.tr("level_detail", lang),
        (utils.tr("general_view", lang), utils.tr("individual_analysis", lang)),
        index=0,
        label_visibility="collapsed"
    )

    st.markdown(f"<p class='sidebar-section-title' style='font-size: 0.8rem; margin-top:5px;'>{utils.tr('global_filters', lang)}</p>", unsafe_allow_html=True)

    is_aggregated_view = (modo_analise == utils.tr("general_view", lang))

    if is_aggregated_view:
        oponentes = [utils.tr("all_opponents", lang)] + sorted(df_games["opponent"].dropna().unique().tolist())
        escolha_oponente = st.selectbox(utils.tr("opponent", lang), oponentes, label_visibility="collapsed")
        df_filtrado, titulo_contexto = utils.filtrar_dados_jogo(df, modo_analise, lang, oponente_selecionado=escolha_oponente)
    else:
        lista_jogos = (
            df_games.loc[df_games["session_date"].notna(), ["session_id", "session_date", "opponent"]]
            .drop_duplicates()
            .sort_values("session_date", ascending=False)
        )
        lista_jogos["label"] = lista_jogos["session_date"].dt.strftime("%d/%m/%Y") + " vs " + lista_jogos["opponent"]

        escolha_label = st.selectbox(utils.tr("select_game", lang), lista_jogos["label"], label_visibility="collapsed")
        id_sessao = lista_jogos.loc[lista_jogos["label"] == escolha_label, "session_id"].iloc[0]

        df_filtrado, _ = utils.filtrar_dados_jogo(df, modo_analise, lang, id_sessao=id_sessao)
        titulo_contexto = f"{utils.tr('analysis_of', lang)} {escolha_label}"
    
    # Translated info message
    st.info(utils.tr("sidebar_info", lang))
    
    st.session_state.lang = lang # Ensure it persists

if df_filtrado.empty:
    st.warning(utils.tr("no_data", lang))
    st.stop()


# MAIN HEADER 
st.markdown(f"""<div class="main-header-container">
    <h1 class="main-header-title">{utils.tr('header_title', lang)}</h1>
    <h3 class="main-header-subtitle">{utils.tr('header_subtitle', lang)}</h3>
</div>""", unsafe_allow_html=True)
st.divider()


# TOP METRICS DASHBOARD
t, g, d, eff = utils.calcular_metricas_topo(df_filtrado)

st.markdown(f"""
<div class="metrics-container">
    <div class="metric-box">
        <div class="metric-label">{utils.tr('metrics_total_shots', lang)}</div>
        <div class="metric-value metric-black">{t}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">{utils.tr('metrics_saves', lang)}</div>
        <div class="metric-value metric-green">{d}</div>
        <div class="metric-badge">{eff:.1f}% {utils.tr('metrics_efficiency', lang)}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">{utils.tr('metrics_goals', lang)}</div>
        <div class="metric-value metric-red">{g}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">{utils.tr('metrics_avg_bpm', lang)}</div>
        <div class="metric-value metric-orange">{df_filtrado['heart_rate'].mean():.0f} <span class="metric-unit">bpm</span></div>
    </div>
    <div class="metric-box">
        <div class="metric-label">{utils.tr('metrics_avg_reaction', lang)}</div>
        <div class="metric-value metric-blue">{df_filtrado['reaction_time_ms'].mean():.0f} <span class="metric-unit">ms</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ZONA 1
st.markdown(f"<div id='zone1'></div><h3 class='zone-header-title'>{utils.tr('zone1_title', lang)}: {titulo_contexto}</h3>", unsafe_allow_html=True)

# FILTROS ZONA 1 - LINHA 1
c1_r1_c1, c1_r1_c2, c1_r1_c3, c1_r1_c4, c1_r1_c5 = st.columns([1.0, 0.1, 2.0, 2.0, 0.5])
with c1_r1_c1:
    st.markdown(f"<span class='f-row-top filter-row-header'>{utils.tr('filter_zone1', lang).replace(' ', '<br>')}</span>", unsafe_allow_html=True)
with c1_r1_c2:
    st.write("")
with c1_r1_c3:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('shooter_pos', lang)}</p>", unsafe_allow_html=True)
    roles = sorted(df_filtrado['shooter_role'].unique().tolist())
    shared_shooter_sel = st.multiselect(utils.tr("shooter_pos", st.session_state.lang), roles, placeholder=utils.tr("all_f", st.session_state.lang), label_visibility="collapsed")
with c1_r1_c4:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('game_minute', lang)}</p>", unsafe_allow_html=True)
    shared_tempo_sel = st.slider(utils.tr("game_minute", lang), 0, 60, (0, 60), label_visibility="collapsed")
with c1_r1_c5: 
     st.write("")


# ZONE 1 FILTERS - ROW 2 (Spatial Detail)
c1_r2_c1, c1_r2_c2, c1_r2_c3, c1_r2_c4, c1_r2_c5, c1_r2_c6, c1_r2_c7 = st.columns([0.3, 0.6, 1.1, 1.1, 2.2, 1.0, 1])
with c1_r2_c1:
      st.markdown("<span class='f-row-bottom'></span>", unsafe_allow_html=True)
with c1_r2_c2:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('points', lang)}</p>", unsafe_allow_html=True)
    mostrar_bolas_local = st.toggle(utils.tr('points', lang), value=True, label_visibility="collapsed")
with c1_r2_c3:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('map_detail', lang)}</p>", unsafe_allow_html=True)
    n_detalhe = st.slider(utils.tr('map_detail', lang), 5, 40, 20, label_visibility="collapsed")
with c1_r2_c4:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('opacity', lang)}</p>", unsafe_allow_html=True)
    n_opacidade = st.slider(utils.tr('opacity', lang), 0.1, 1.0, 0.6, label_visibility="collapsed")
with c1_r2_c5:
    st.write("") 
with c1_r2_c6:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('chart_order', lang)}</p>", unsafe_allow_html=True)
    ordem_sel = st.selectbox(utils.tr('chart_order', lang), [utils.tr("ascending", lang), utils.tr("descending", lang)], index=0, label_visibility="collapsed")
    asc_order = (ordem_sel == utils.tr("ascending", lang))
with c1_r2_c7:
    st.write("")


# FILTERING LOGIC
df_viz_filtrado = utils.filtrar_zona_1(df_filtrado, shared_shooter_sel, shared_tempo_sel)

# ZONE 1 CHARTS (Spatial)
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='subtitulo-visualizacao'>{utils.tr('heatmap_title', lang)}</div>", unsafe_allow_html=True)
    df_golos = df_viz_filtrado[df_viz_filtrado['outcome'] == 'GOAL'].copy()
    if not df_golos.empty:
        st.plotly_chart(charts.gerar_figura_baliza(df_golos, n_detalhe, n_opacidade, mostrar_bolas_local, "assets/baliza.png", theme_colors, lang), use_container_width=True, config={'displayModeBar': False})
        c_grid_l, c_grid_c, c_grid_r = st.columns([0.1, 5.8, 0.1])
        with c_grid_c:
            with st.popover(utils.tr('defense_rate_zone', lang), use_container_width=True):
                st.plotly_chart(charts.gerar_grelha_3x3(df_viz_filtrado, theme_colors, lang), use_container_width=True, config={'displayModeBar': False})
    else:
        st.info(utils.tr('no_shots', lang))

with col2:
    st.markdown(f"<div class='subtitulo-visualizacao'>{utils.tr('efficiency_pos', lang)}</div>", unsafe_allow_html=True)
    df_role_stats = utils.calcular_estatisticas_posicao(df_viz_filtrado, asc_order)
    if not df_role_stats.empty:
        st.plotly_chart(charts.gerar_barras_posicao(df_role_stats, asc_order, theme_colors, lang), use_container_width=True, config={'displayModeBar': False})
        _, c2_pop = st.columns([3, 2])
        with c2_pop:
            with st.popover(utils.tr('position_map', lang), use_container_width=True):
                st.image("assets/positions.png", use_container_width=True)
    else:
        st.info(utils.tr('no_data', lang))

st.markdown("---")

# ZONA 2
if is_aggregated_view:
    st.markdown(f"<div id='zone2'></div><h3 class='zone-header-title-no-margin'>{utils.tr('zone2_title', lang)}</h3>", unsafe_allow_html=True)
    st.write("")
    df_temp, game_dates = utils.preparar_matriz_temporal(df_filtrado)

    # FILTROS ZONA 2
    c2_r1_c1, c2_r1_c2, c2_r1_c3, c2_r1_c4, c2_r1_c5, c2_r1_c6 = st.columns([1.2, 0.5, 2.0, 1.8, 1.6, 0.5])
    with c2_r1_c1:
        st.markdown(f"<span class='f-row-single filter-row-header'>{utils.tr('filter_zone2', lang).replace(' ', '<br>')}</span>", unsafe_allow_html=True)
    with c2_r1_c2:
        st.write("")
    with c2_r1_c3:
        st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('shot_type', lang)}</p>", unsafe_allow_html=True)
        tipos_disponiveis = sorted(df_temp['shot_type'].unique().tolist())
        sel_tipos = st.multiselect(utils.tr('shot_type', st.session_state.lang), tipos_disponiveis, placeholder=utils.tr("all_m", st.session_state.lang), label_visibility="collapsed", key="z2_tipos")
    with c2_r1_c4:
        st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('game_range', lang)}</p>", unsafe_allow_html=True)
        max_jogos = len(game_dates)
        sel_jogos = st.slider(utils.tr('game_range', lang), 1, max_jogos, (1, max_jogos), label_visibility="collapsed", key="z2_jogos")
    with c2_r1_c5:
        st.markdown(f"<p class='filter-label-margin-5'>% {utils.tr('metrics_efficiency', lang)}</p>", unsafe_allow_html=True)
        sel_eficacia = st.slider(utils.tr('metrics_efficiency', lang), 0, 100, (0, 100), label_visibility="collapsed", key="z2_eficacia")
    with c2_r1_c6:
        st.write("")
    
    df_temp = utils.filtrar_zona_2(df_filtrado, sel_tipos, sel_jogos)
    st.markdown(f"<div class='subtitulo-visualizacao'>{utils.tr('matrix_title', lang)}</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.gerar_matriz_eficacia(df_temp, sel_eficacia, theme_colors, lang), use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

# ZONA 3
st.markdown(f"<div id='zone3'></div><h3 class='zone-header-title'>{utils.tr('zone3_title', lang)}</h3>", unsafe_allow_html=True)
st.write("")

# FILTROS ZONA 3 - LINHA 1
c3_r1_c1, c3_r1_c2, c3_r1_c3, c3_r1_c4, c3_r1_c5, c3_r1_c6 = st.columns([1.0, 0.1, 2.0, 1.5, 1.5, 0.1])
with c3_r1_c1:
    st.markdown(f"<span class='f-row-top filter-row-header'>{utils.tr('filter_zone3', lang).replace(' ', '<br>')}</span>", unsafe_allow_html=True)
with c3_r1_c2: st.write("")
with c3_r1_c3:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('shot_type', lang)}</p>", unsafe_allow_html=True)
    tipos_z3 = sorted(df_filtrado['shot_type'].unique().tolist())
    sel_tipos_z3 = st.multiselect(utils.tr('shot_type', st.session_state.lang), tipos_z3, placeholder=utils.tr("all_m", st.session_state.lang), label_visibility="collapsed", key="z3_tipos")
with c3_r1_c4:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('shooter_pos', lang)}</p>", unsafe_allow_html=True)
    roles_z3 = sorted(df_filtrado['shooter_role'].unique().tolist())
    sel_roles_z3 = st.multiselect(utils.tr('shooter_pos', st.session_state.lang), roles_z3, placeholder=utils.tr("all_f", st.session_state.lang), label_visibility="collapsed", key="z3_roles")
with c3_r1_c5:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('game_minute', lang)}</p>", unsafe_allow_html=True)
    sel_minuto_z3 = st.slider(utils.tr('game_minute', lang), 0, 60, (0, 60), label_visibility="collapsed", key="z3_minuto")
with c3_r1_c6: st.write("")

# FILTROS ZONA 3 - LINHA 2
c3_r2_c1, c3_r2_c2, c3_r2_c3, c3_r2_c4, c3_r2_c5, c3_r2_c6, c3_r2_c7 = st.columns([0.1, 0.3, 2.0, 1.0, 2.0, 1.2, 0.5])
with c3_r2_c1:
    st.markdown("<span class='f-row-bottom'></span>", unsafe_allow_html=True)
with c3_r2_c2: st.write("")
with c3_r2_c3:
    st.markdown(f"<p class='filter-label-margin-5'>% {utils.tr('metrics_efficiency', lang)}</p>", unsafe_allow_html=True)
    sel_efic_range = st.slider(utils.tr('metrics_efficiency', lang), 0, 100, (0, 100), label_visibility="collapsed", key="z3_efic_range")
with c3_r2_c4: st.write("")
with c3_r2_c5:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('metrics_avg_reaction', lang)} (ms)</p>", unsafe_allow_html=True)
    sel_reacao_range = st.slider(utils.tr('metrics_avg_reaction', lang), 200, 500, (200, 500), label_visibility="collapsed", key="z3_reacao_range")
with c3_r2_c6:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('chart_order', lang)}</p>", unsafe_allow_html=True)
    ordem_z3 = st.selectbox(utils.tr('chart_order', lang), [utils.tr("ascending", lang), utils.tr("descending", lang)], index=1, label_visibility="collapsed", key="z3_ordem")
with c3_r2_c7: st.write("")

# PROCESSAMENTO ZONA 3
df_z3_filtrado = utils.filtrar_zona_3(df_filtrado, sel_tipos_z3, sel_roles_z3, sel_minuto_z3)
df_type_stats = utils.calcular_estatisticas_tecnicas(df_z3_filtrado)

# GRÁFICOS ZONA 3
col_tec1, col_tec2 = st.columns(2)
with col_tec1:
    st.markdown(f"<div class='subtitulo-visualizacao'>{utils.tr('ranking_efficiency', lang)}</div>", unsafe_allow_html=True)
    if not df_type_stats.empty and len(df_type_stats) > 0:
        try:
            df_eff = df_type_stats[df_type_stats['Eficacia'].between(sel_efic_range[0], sel_efic_range[1])].copy()
            if not df_eff.empty:
                asc_eff = True if ordem_z3 == utils.tr("ascending", lang) else False
                df_eff = df_eff.sort_values('Eficacia', ascending=asc_eff)
                st.plotly_chart(charts.gerar_ranking_eficacia(df_eff, ordem_z3, theme_colors, lang), use_container_width=True, config={'displayModeBar': False})
            else:
                st.info(utils.tr('no_shots', lang))
        except Exception:
            st.info(utils.tr('no_data', lang))
    else:
        st.info(utils.tr('no_data', lang))

with col_tec2:
    st.markdown(f"<div class='subtitulo-visualizacao'>{utils.tr('avg_reaction_speed', lang)}</div>", unsafe_allow_html=True)
    if not df_type_stats.empty and len(df_type_stats) > 0:
        try:
            df_react = df_type_stats[df_type_stats['Reacao_Media'].between(sel_reacao_range[0], sel_reacao_range[1])].copy()
            if not df_react.empty:
                asc_react = True if ordem_z3 == utils.tr("ascending", lang) else False
                df_react = df_react.sort_values('Reacao_Media', ascending=asc_react)
                st.plotly_chart(charts.gerar_ranking_reacao(df_react, ordem_z3, theme_colors, lang), use_container_width=True, config={'displayModeBar': False})
            else:
                st.info(utils.tr('no_shots', lang))
        except Exception:
            st.info(utils.tr('no_data', lang))
    else:
        st.info(utils.tr('no_data', lang))

st.markdown("---")

# ZONA 4
st.markdown(f"<div id='zone4'></div><h3 class='zone-header-title'>{utils.tr('zone4_title', lang)}</h3>", unsafe_allow_html=True)
st.write("")

# FILTROS ZONA 4 - LINHA 1
c4_r1_c1, c4_r1_c2, c4_r1_c3, c4_r1_c4, c4_r1_c5, c4_r1_c6, c4_r1_c7 = st.columns([1.2, 0.5, 2.8, 1.6, 1.6, 1.0, 0.5])
with c4_r1_c1:
    st.markdown(f"<span class='f-row-top filter-row-header'>{utils.tr('filter_zone4', lang).replace(' ', '<br>')}</span>", unsafe_allow_html=True)
with c4_r1_c2: st.write("")
with c4_r1_c3:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('general_filters', lang)}</p>", unsafe_allow_html=True)
    c4_sub1, c4_sub2 = st.columns(2)
    with c4_sub1:
        roles_z4 = sorted(df_filtrado['shooter_role'].dropna().unique().tolist()) if 'shooter_role' in df_filtrado.columns else []
        sel_role_z4 = st.multiselect(utils.tr('shooter_pos', st.session_state.lang), roles_z4, placeholder=utils.tr('all_f', st.session_state.lang), label_visibility="collapsed", key="z4_roles")
    with c4_sub2:
        tipos_z4 = sorted(df_filtrado['shot_type'].dropna().unique().tolist()) if 'shot_type' in df_filtrado.columns else []
        sel_tipo_z4 = st.multiselect(utils.tr('shot_type', st.session_state.lang), tipos_z4, placeholder=utils.tr('all_m', st.session_state.lang), label_visibility="collapsed", key="z4_tipos")
with c4_r1_c4:
     st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('bpm', lang)}</p>", unsafe_allow_html=True)
     hr_min = int(df_filtrado['heart_rate'].min()) if 'heart_rate' in df_filtrado.columns and not df_filtrado['heart_rate'].isna().all() else 40
     hr_max = int(df_filtrado['heart_rate'].max()) if 'heart_rate' in df_filtrado.columns and not df_filtrado['heart_rate'].isna().all() else 200
     sel_bpm = st.slider(utils.tr('bpm', lang), hr_min, hr_max, (hr_min, hr_max), label_visibility="collapsed", key="z4_bpm")
with c4_r1_c5:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('avg_reaction_speed', lang)}</p>", unsafe_allow_html=True)
    rt_min = int(df_filtrado['reaction_time_ms'].min()) if 'reaction_time_ms' in df_filtrado.columns and not df_filtrado['reaction_time_ms'].isna().all() else 150
    rt_max = int(df_filtrado['reaction_time_ms'].max()) if 'reaction_time_ms' in df_filtrado.columns and not df_filtrado['reaction_time_ms'].isna().all() else 700
    sel_reaction = st.slider(utils.tr('avg_reaction_speed', lang), rt_min, rt_max, (rt_min, rt_max), label_visibility="collapsed", key="z4_reaction")
with c4_r1_c6:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('game_minute', lang)}</p>", unsafe_allow_html=True)
    sel_minuto_z4 = st.slider(utils.tr('game_minute', lang), 0, 60, (0, 60), label_visibility="collapsed", key="z4_minuto")
with c4_r1_c7: st.write("")

# FILTROS ZONA 4 - LINHA 2
c4_r2_c1, c4_r2_c2, c4_r2_c3, c4_r2_c4, c4_r2_c5, c4_r2_c6 = st.columns([0.1, 0.5, 2.2, 0.5, 2.2, 0.5])
with c4_r2_c1:
    st.markdown("<span class='f-row-bottom'></span>", unsafe_allow_html=True)
with c4_r2_c2: st.write("")
with c4_r2_c3:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('outcome', lang)}</p>", unsafe_allow_html=True)
    outcomes = sorted(df_filtrado['outcome'].dropna().unique().tolist()) if 'outcome' in df_filtrado.columns else []
    sel_outcome_z4 = st.multiselect(utils.tr('outcome', st.session_state.lang), outcomes, default=outcomes, placeholder=utils.tr("all_m", st.session_state.lang), label_visibility="collapsed", key="z4_outcome")
with c4_r2_c4: st.write("")
with c4_r2_c5:
    st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('show_lines', lang)}</p>", unsafe_allow_html=True)
    c4_tog1, c4_tog2 = st.columns(2)
    with c4_tog1:
        show_bpm_line = st.checkbox(utils.tr('bpm', lang), value=True, key="z4_show_bpm")
    with c4_tog2:
        show_reaction_line = st.checkbox(utils.tr('metrics_avg_reaction', lang), value=True, key="z4_show_reaction")
with c4_r2_c6: st.write("")

# PROCESSAMENTO ZONA 4
df_z4_filtrado = utils.filtrar_zona_4(df_filtrado, sel_bpm, sel_reaction, sel_role_z4, sel_tipo_z4, sel_minuto_z4)

# GRÁFICOS ZONA 4
c_fisio1, c_fisio2 = st.columns(2)
with c_fisio1:
    st.markdown(f"<div class='subtitulo-visualizacao'>{utils.tr('correlation_title', lang)}</div>", unsafe_allow_html=True)
    df_left = df_z4_filtrado.copy()
    if 'outcome' in df_left.columns and sel_outcome_z4:
        df_left = df_left[df_left['outcome'].isin(sel_outcome_z4)]
    if df_left.empty:
        st.info(utils.tr('no_data', lang))
    else:
        st.plotly_chart(charts.gerar_scatter_correlacao(df_left, theme_colors, lang), use_container_width=True, config={'displayModeBar': False})

with c_fisio2:
    st.markdown(f"<div class='subtitulo-visualizacao'>{utils.tr('temporal_evolution', lang)}</div>", unsafe_allow_html=True)
    df_right = df_z4_filtrado.sort_values('game_minute')
    if df_right.empty:
        st.info(utils.tr('no_data', lang))
    else:
        st.plotly_chart(charts.gerar_evolucao_temporal(df_right, show_bpm_line, show_reaction_line, theme_colors, lang), use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# ZONA 5: PREVISÃO (ML)
st.markdown(f"<div id='zone5'></div><h3 class='zone-header-title'>{utils.tr('zone5_title', lang)}</h3>", unsafe_allow_html=True)

if model:
    # FILTROS ZONA 5
    c5_r1_c1, c5_r1_c2, c5_r1_c3, c5_r1_c4, c5_r1_c5, c5_r1_c6 = st.columns([1.0, 0.1, 1.5, 1.5, 1.5, 0.1])
    with c5_r1_c1:
        st.markdown(f"<span class='f-row-single filter-row-header'>{utils.tr('filter_zone5', lang).replace(' ', '<br>')}</span>", unsafe_allow_html=True)
    with c5_r1_c2: st.write("")
    with c5_r1_c3:
        st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('shooter_pos', lang)}</p>", unsafe_allow_html=True)
        p_role = st.selectbox(utils.tr("shooter_pos", lang), encoders['shooter_role'].classes_, label_visibility="collapsed", key="z5_role")
        st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('shot_type', lang)}</p>", unsafe_allow_html=True)
        p_type = st.selectbox(utils.tr("shot_type", lang), encoders['shot_type'].classes_, label_visibility="collapsed", key="z5_type")
    with c5_r1_c4:
        st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('technique', lang)}</p>", unsafe_allow_html=True)
        # Professional technique mapping
        tech_opts = sorted(encoders['technique'].classes_)
        tech_display = {t: utils.mapear_tecnica(t, lang) for t in tech_opts}
        p_tech = st.selectbox(utils.tr('technique', lang), tech_opts, format_func=lambda x: tech_display[x], label_visibility="collapsed", key="z5_tech")
        
        st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('velocity', lang)} (km/h)</p>", unsafe_allow_html=True)
        p_vel = st.slider(utils.tr('velocity', lang), 50, 130, 90, label_visibility="collapsed", key="z5_vel")
    with c5_r1_c5:
        st.markdown(f"<p class='filter-label-margin-5'>{utils.tr('bpm', lang)}</p>", unsafe_allow_html=True)
        p_bpm = st.slider(utils.tr('bpm', lang), 100, 200, 150, label_visibility="collapsed", key="z5_bpm")
    with c5_r1_c6: st.write("")

    base_feat = {
        'shooter_role': p_role,
        'shot_type': p_type,
        'technique': p_tech,
        'velocity_kmh': p_vel,
        'heart_rate': p_bpm
    }

    # CALCULATE AVERAGE PROBABILITY
    import numpy as np
    y_points = 10
    z_points = 10
    prob_list = []
    for ty in np.linspace(0.2, 2.8, y_points):
        for tz in np.linspace(0.2, 1.8, z_points):
            tf = base_feat.copy()
            tf['target_y'] = ty
            tf['target_z'] = tz
            p = utils.prever_probabilidade(model, encoders, tf)
            dist = np.sqrt((ty - 1.5)**2 + (tz - 1.0)**2) / 1.8 
            p = p * (1 - 0.2 * dist)
            prob_list.append(p)
    global_prob = sum(prob_list) / len(prob_list)

    # FINAL 3-COLUMN LAYOUT
    st.markdown("<br>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 1.3], gap="medium")
    
    with f_col1:
        # LEFT: PROBABILITY HEATMAP
        fig_prob = charts.gerar_heatmap_probabilidade(model, encoders, base_feat, theme_colors, lang)
        fig_prob.update_layout(height=320, margin=dict(t=30, r=10, b=30, l=40))
        st.plotly_chart(fig_prob, use_container_width=True, config={'displayModeBar': False})
        
    with f_col2:
        # CENTER: MAIN PROBABILITY METRIC (AVERAGE)
        st.markdown(f"""
        <div style="background: {theme_colors['filter_row_bg']}; padding: 30px; border-radius: 15px; border: 2px solid {theme_colors['filter_row_border']}; text-align: center; height: 320px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <p style="margin: 0; font-size: 1.1rem; color: {theme_colors['metric_label']}; font-weight: 600; letter-spacing: 1px;">{utils.tr('prediction_probability', lang).upper()} (MÉDIA)</p>
            <h1 style="margin: 15px 0; font-size: 5.0rem; color: #2e7d32; font-weight: 800; line-height: 1;">{global_prob*100:.1f}%</h1>
            <p style="margin: 0; font-size: 0.8rem; color: #2e7d32; opacity: 0.8; font-weight: 500;">✓ Média em Toda a Baliza</p>
        </div>
        """, unsafe_allow_html=True)
        
    with f_col3:
        # RIGHT: PERMANENT TECHNIQUE GUIDE
        st.markdown(f"""
        <div style="background: {theme_colors['filter_row_bg']}; padding: 25px; border-radius: 12px; border: 1px solid {theme_colors['filter_row_border']}; height: 320px; overflow-y: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
            <h4 style="margin-top: 0; color: #d32f2f; font-size: 1rem; border-bottom: 1px solid rgba(0,0,0,0.1); padding-bottom: 8px;">
                {utils.tr('glossary_title', lang)}
            </h4>
            <div style="color: {theme_colors['text']}; line-height: 1.45; font-size: 0.88rem; margin-top: 10px;">
                {utils.obter_glossario_tecnico(lang).replace("- ", "<div style='margin-bottom: 6px;'>• ").replace("\n", "</div>")}
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.error(utils.tr("ml_not_available", lang))

st.markdown("---")


# FOOTER / DATA LOG
with st.expander(utils.tr('raw_data_expand', lang)):
    st.dataframe(df_filtrado.sort_values('game_minute')[['game_minute', 'opponent', 'shooter_role', 'shot_type', 'technique', 'outcome', 'heart_rate', 'reaction_time_ms', 'velocity_kmh']])

# PDF EXPORT BUTTON
st.markdown("<br>", unsafe_allow_html=True)
col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 1])
with col_exp2:
    report_metrics = {
        utils.tr("metrics_total_shots", lang): t,
        utils.tr("metrics_saves", lang): d,
        utils.tr("metrics_goals", lang): g,
        utils.tr("metrics_efficiency", lang): f"{eff:.1f}%",
    }
    
    # ACTIVE FILTERS FOR EXPORT
    active_filters = []
    if is_aggregated_view:
        active_filters.append(f"{utils.tr('level_detail', lang)}: {utils.tr('general_view', lang)}")
        active_filters.append(f"{utils.tr('opponent', lang)}: {escolha_oponente}")
    else:
        active_filters.append(f"{utils.tr('level_detail', lang)}: {utils.tr('individual_analysis', lang)}")
        active_filters.append(f"Jogo: {escolha_label}")
    active_filters.append(f"{utils.tr('game_minute', lang)}: {shared_tempo_sel[0]}-{shared_tempo_sel[1]} min")

    # GENERATE ALL VISUAL DASHBOARD BLOCKS (Zones 1-4 only)
    pdf_figures = []

    # ZONE 1 – Spatial
    row1 = []
    try:
        f_grid = charts.gerar_grelha_3x3(df_viz_filtrado, theme_colors, lang)
        row1.append({'title': utils.tr('defense_rate_zone', lang), 'fig': f_grid, 'zone_title': utils.tr('zone1_title', lang)})
    except Exception: pass
    try:
        if 'df_role_stats' in locals() and not df_role_stats.empty:
            f_pos = charts.gerar_barras_posicao(df_role_stats, asc_order, theme_colors, lang)
            row1.append({'title': utils.tr('efficiency_pos', lang), 'fig': f_pos})
    except Exception: pass
    if row1: pdf_figures.append(row1)

    # ZONE 2 – Temporal Matrix (aggregated only)
    try:
        if is_aggregated_view:
            f_matrix = charts.gerar_matriz_eficacia(utils.filtrar_zona_2(df_filtrado, sel_tipos, sel_jogos), (0, 100), theme_colors, lang)
            pdf_figures.append([{'title': utils.tr('matrix_title', lang), 'fig': f_matrix,
                                  'full_width': True, 'zone_title': utils.tr('zone2_title', lang)}])
    except Exception: pass

    # ZONE 3 – Technical
    row3 = []
    try:
        if 'df_type_stats' in locals() and not df_type_stats.empty:
            df_eff_pdf = df_type_stats[df_type_stats['Eficacia'].between(sel_efic_range[0], sel_efic_range[1])].copy()
            if not df_eff_pdf.empty:
                f_eff = charts.gerar_ranking_eficacia(df_eff_pdf, ordem_z3, theme_colors, lang)
                row3.append({'title': utils.tr('ranking_efficiency', lang), 'fig': f_eff,
                             'zone_title': utils.tr('zone3_title', lang)})
            df_react_pdf = df_type_stats[df_type_stats['Reacao_Media'].between(sel_reacao_range[0], sel_reacao_range[1])].copy()
            if not df_react_pdf.empty:
                f_react = charts.gerar_ranking_reacao(df_react_pdf, ordem_z3, theme_colors, lang)
                row3.append({'title': utils.tr('avg_reaction_speed', lang), 'fig': f_react})
        if row3: pdf_figures.append(row3)
    except Exception: pass

    # ZONE 4 – Biometrics
    row4 = []
    try:
        if 'df_z4_filtrado' in locals() and not df_z4_filtrado.empty:
            f_corr = charts.gerar_scatter_correlacao(df_z4_filtrado, theme_colors, lang)
            f_evol = charts.gerar_evolucao_temporal(df_z4_filtrado.sort_values('game_minute'),
                                                    show_bpm_line, show_reaction_line, theme_colors, lang)
            row4.append({'title': utils.tr('correlation_title', lang), 'fig': f_corr,
                         'zone_title': utils.tr('zone4_title', lang)})
            row4.append({'title': utils.tr('temporal_evolution', lang), 'fig': f_evol})
        if row4: pdf_figures.append(row4)
    except Exception: pass

    pdf_bytes = utils.gerar_pdf_resumo(df_filtrado, lang, titulo_contexto, active_filters, report_metrics, figure_rows=pdf_figures)
    st.download_button(
        label=utils.tr("export_report", lang),
        data=pdf_bytes,
        file_name=f"Handball_Twin_Report_{lang}.pdf",
        mime="application/pdf",
        use_container_width=True
    )