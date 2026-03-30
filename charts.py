import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional
import utils

def gerar_figura_baliza(df_golos: pd.DataFrame, n_detalhe: int, n_opacidade: float, mostrar_bolas: bool, img_path: str, theme_colors: Dict[str, str], lang: str = "pt"):
    """
    Generates the 2D Goal Heatmap with optional markers for shots.
    """
    fig = go.Figure()
    try:
        img = Image.open(img_path)
        fig.add_layout_image(dict(
            source=img, xref="x", yref="y", x=-0.18, y=2.27,
            sizex=3.45, sizey=2.35, sizing="stretch", opacity=1.0, layer="below"
        ))
    except:
        fig.add_shape(type="rect", x0=0, y0=0, x1=3, y1=2, line=dict(color="White", width=4))

    fig.add_trace(go.Histogram2dContour(
        x=df_golos['target_y'], y=df_golos['target_z'],
        colorscale='Jet', ncontours=n_detalhe, showscale=False,
        hoverinfo='none', opacity=n_opacidade,
        xbins=dict(start=-0.15, end=3.15, size=0.2), 
        ybins=dict(start=-0.15, end=2.15, size=0.2)
    ))

    if mostrar_bolas:
        fig.add_trace(go.Scatter(
            x=df_golos['target_y'], y=df_golos['target_z'],
            mode='markers',
            marker=dict(color='white', size=7, opacity=0.9, line=dict(width=1, color='black')),
            text=df_golos.apply(lambda row: f"{utils.tr('metrics_goals', lang)} ({row['game_minute']} min)<br>Shooter: {row['shooter_role']}", axis=1),
            hoverinfo='text'
        ))

    fig.update_layout(
        xaxis=dict(range=[-0.5, 3.5], showgrid=False, zeroline=False, visible=False, fixedrange=True),
        yaxis=dict(range=[-0.1, 2.45], showgrid=False, zeroline=False, visible=False, fixedrange=True),
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        margin=dict(l=10, r=10, t=0, b=10), height=450, showlegend=False
    )
    return fig


def gerar_grelha_3x3(df_grid: pd.DataFrame, theme_colors: Dict[str, str], lang: str = "pt"):
    """
    Generates a 3x3 text-based grid showing save rates for goal sectors.
    """
    # Zone labels based on language
    y_labels = [utils.tr('left', lang) if 'left' in utils.TRANSLATIONS[lang] else 'Left', 
                utils.tr('center', lang) if 'center' in utils.TRANSLATIONS[lang] else 'Center', 
                utils.tr('right', lang) if 'right' in utils.TRANSLATIONS[lang] else 'Right']
    
    # Simple fallback if direct keys don't exist yet in utils
    if lang == "pt":
        y_labels = ['Esquerda', 'Centro', 'Direita']
        z_labels = ['Base', 'Meio', 'Topo']
    else:
        y_labels = ['Left', 'Center', 'Right']
        z_labels = ['Bottom', 'Middle', 'Top']

    # Create the coordinate zones for Y and Z axes
    df_grid['y_zone'] = pd.cut(df_grid['target_y'], bins=[0, 1, 2, 3.01], labels=y_labels, include_lowest=True)
    df_grid['z_zone'] = pd.cut(df_grid['target_z'], bins=[0, 0.67, 1.33, 2.01], labels=z_labels, include_lowest=True)

    grid_stats = df_grid.groupby(['z_zone', 'y_zone'], observed=False).apply(
        lambda x: pd.Series({
            'Sucesso': len(x[x['outcome'].isin(['SAVE', 'MISS'])]), 
            'TotalPosicao': len(x)
        }), include_groups=False
    ).reset_index()

    grid_stats['TaxaSucesso'] = grid_stats.apply(
        lambda row: (row['Sucesso'] / row['TotalPosicao'] * 100) if row['TotalPosicao'] > 0 else 0, 
        axis=1
    )

    text_matrix = grid_stats.pivot(index='z_zone', columns='y_zone', values='TaxaSucesso').fillna(0)
    success_matrix = grid_stats.pivot(index='z_zone', columns='y_zone', values='Sucesso').fillna(0)
    totals_matrix = grid_stats.pivot(index='z_zone', columns='y_zone', values='TotalPosicao').fillna(0)

    fig = go.Figure()
    text_color = theme_colors.get('text', '#000000')

    for i, z_l in enumerate(z_labels):
        for j, y_l in enumerate(y_labels):
            eff = text_matrix.loc[z_l, y_l]
            succ = success_matrix.loc[z_l, y_l]
            tot = totals_matrix.loc[z_l, y_l]
            color_eff = "#2e7d32" if eff >= 50 else "#d32f2f"
            fig.add_annotation(
                x=j, y=i, showarrow=False,
                text=f"<b style='color:{color_eff}'>{eff:.0f}%</b><br><span style='color:{text_color}; font-size:12px'>({int(succ)}/{int(tot)})</span>",
                font=dict(size=18, color=text_color)
            )

    line_color = theme_colors.get('text', '#000000')
    for p in [0.5, 1.5]:
        fig.add_shape(type="line", x0=p, y0=-0.5, x1=p, y1=2.5, line=dict(color=line_color, width=1, dash="dash"))
        fig.add_shape(type="line", x0=-0.5, y0=p, x1=2.5, y1=p, line=dict(color=line_color, width=1, dash="dash"))

    fig.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        height=350,
        margin=dict(l=80, r=40, t=10, b=80),
        xaxis=dict(showgrid=False, zeroline=False, tickvals=[0, 1, 2], ticktext=y_labels, tickfont=dict(size=14, color=text_color), range=[-0.8, 2.8]),
        yaxis=dict(showgrid=False, zeroline=False, tickvals=[0, 1, 2], ticktext=z_labels, tickfont=dict(size=14, color=text_color), range=[-0.6, 2.6])
    )
    return fig


def gerar_barras_posicao(df_role_stats: pd.DataFrame, asc_order: bool, theme_colors: Dict[str, str], lang: str = "pt"):
    """
    Generates a horizontal bar chart for efficiency by shooter role.
    """
    text_color = theme_colors.get('text', '#000000')
    fig = px.bar(df_role_stats, x='Eficacia', y='shooter_role', orientation='h',
                 color='Eficacia', color_continuous_scale='RdYlGn',
                 labels={'shooter_role': utils.tr('shooter_pos', lang), 'Eficacia': utils.tr('metrics_efficiency', lang) + ' (%)'})
    
    fig.add_trace(go.Scatter(
        x=df_role_stats['Eficacia'], y=df_role_stats['shooter_role'],
        text=df_role_stats.apply(lambda x: f" {x['Eficacia']:.0f}%  ({int(x['Defesas'])}/{int(x['Total'])})", axis=1),
        mode='text', textposition='middle right',
        textfont=dict(color=text_color, size=13, weight='bold'),
        showlegend=False, hoverinfo='skip', cliponaxis=False
    ))

    fig.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        font_color=text_color,
        xaxis=dict(title=dict(text=utils.tr('metrics_efficiency', lang) + " (%)", font=dict(color=text_color)), 
                   range=[0, 135], showgrid=True, gridcolor='rgba(128,128,128,0.2)', tickfont=dict(color=text_color)),
        yaxis=dict(title=dict(text=utils.tr('shooter_pos', lang), font=dict(color=text_color)), tickfont=dict(color=text_color)),
        coloraxis_colorbar=dict(title=dict(text=" (%)", font=dict(color=text_color)), tickfont=dict(color=text_color)),
        height=450, margin=dict(t=10, r=20, b=10, l=10)
    )
    return fig


def gerar_matriz_eficacia(df_temp: pd.DataFrame, sel_eficacia: tuple, theme_colors: Dict[str, str], lang: str = "pt"):
    """
    Generates an interactive heatmap matrix (Shot Type vs. Game Sequence).
    """
    matrix_data = df_temp.groupby(['shot_type', 'game_seq'], observed=True).apply(
        lambda x: (len(x[x['outcome'] == 'SAVE']) / len(x) * 100) if len(x) > 0 else None, include_groups=False
    ).reset_index(name='Eficacia')

    if sel_eficacia != (0, 100):
        matrix_data.loc[~matrix_data['Eficacia'].between(sel_eficacia[0], sel_eficacia[1]), 'Eficacia'] = None

    pivot_matrix = matrix_data.pivot(index='shot_type', columns='game_seq', values='Eficacia')
    text_color = theme_colors.get('text', '#000000')

    fig_matrix = go.Figure(data=go.Heatmap(
        z=pivot_matrix.values,
        x=pivot_matrix.columns,
        y=pivot_matrix.index,
        colorscale='RdYlGn',
        zmin=0, zmax=100,
        colorbar=dict(
            title=dict(text=utils.tr('metrics_efficiency', lang) + " (%)", font=dict(color=text_color)),
            thickness=15,
            tickfont=dict(color=text_color)
        )
    ))

    fig_matrix.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        font_color=text_color,
        xaxis=dict(
            title=dict(text=utils.tr('game_range', lang), font=dict(color=text_color)),
            tickfont=dict(color=text_color),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title=dict(text=utils.tr('shot_type', lang), font=dict(color=text_color)),
            tickfont=dict(color=text_color),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        height=400,
        margin=dict(t=10, r=20, b=10, l=10)
    )
    return fig_matrix


def gerar_ranking_eficacia(df_eff: pd.DataFrame, asc_eff: str, theme_colors: Dict[str, str], lang: str = "pt"):
    """
    Generates a vertical bar chart ranking efficiency by shot type.
    """
    text_color = theme_colors.get('text', '#000000')
    max_eficacia = df_eff['Eficacia'].max()
    y_max_eff = max(105, max_eficacia * 1.15) if not pd.isna(max_eficacia) else 105
    
    fig_eff = px.bar(
        df_eff, x='shot_type', y='Eficacia',
        color='Eficacia', color_continuous_scale='Blues',
        text=df_eff['Eficacia'].apply(lambda x: f"{x:.0f}%")
    )
    fig_eff.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        font_color=text_color,
        xaxis=dict(title=dict(text=utils.tr('shot_type', lang), font=dict(color=text_color)), tickfont=dict(color=text_color)),
        yaxis=dict(
            title=dict(text="% " + utils.tr('metrics_efficiency', lang), font=dict(color=text_color)), 
            range=[0, y_max_eff], 
            tickfont=dict(color=text_color),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        showlegend=False,
        coloraxis_showscale=False, margin=dict(t=10, r=10, b=10, l=10)
    )
    fig_eff.update_traces(textposition='outside', textfont=dict(color=text_color, size=12, weight='bold'))
    return fig_eff


def gerar_ranking_reacao(df_react: pd.DataFrame, asc_react: str, theme_colors: Dict[str, str], lang: str = "pt"):
    """
    Generates a vertical bar chart ranking reaction time by shot type.
    """
    text_color = theme_colors.get('text', '#000000')
    max_reacao = df_react['Reacao_Media'].max()
    y_max_react = max(520, max_reacao * 1.15) if not pd.isna(max_reacao) else 520
    
    fig_react = px.bar(
        df_react, x='shot_type', y='Reacao_Media',
        color='Reacao_Media', color_continuous_scale='Viridis',
        text=df_react['Reacao_Media'].apply(lambda x: f"{x:.0f} ms")
    )
    fig_react.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        font_color=text_color,
        xaxis=dict(title=dict(text=utils.tr('shot_type', lang), font=dict(color=text_color)), tickfont=dict(color=text_color)),
        yaxis=dict(
            title=dict(text="ms", font=dict(color=text_color)), 
            range=[200, y_max_react], 
            tickfont=dict(color=text_color),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        showlegend=False,
        coloraxis_showscale=False, margin=dict(t=10, r=10, b=10, l=10)
    )
    fig_react.update_traces(textposition='outside', textfont=dict(color=text_color, size=12, weight='bold'))
    return fig_react


def gerar_scatter_correlacao(df_left: pd.DataFrame, theme_colors: Dict[str, str], lang: str = "pt"):
    """
    Generates a scatter plot showing the correlation between Heart Rate and Reaction Time.
    Includes the Pearson correlation coefficient calculated in situ or provided.
    """
    text_color = theme_colors.get('text', '#000000')
    r_val = utils.calcular_correlacao_pearson(df_left)
    
    fig_corr = px.scatter(
        df_left,
        x='heart_rate',
        y='reaction_time_ms',
        color='outcome',
        color_discrete_map={'GOAL': '#ff4b4b', 'SAVE': '#2e7d32', 'MISS': 'gray'},
        hover_data=['game_minute', 'shooter_role', 'shot_type'],
        labels={'heart_rate': utils.tr('bpm', lang), 'reaction_time_ms': utils.tr('avg_reaction_speed', lang), 'outcome': utils.tr('outcome', lang)}
    )
    
    fig_corr.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        font_color=text_color,
        xaxis=dict(title=dict(font=dict(color=text_color)), tickfont=dict(color=text_color), gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(title=dict(font=dict(color=text_color)), tickfont=dict(color=text_color), gridcolor='rgba(128,128,128,0.2)'),
        legend=dict(
            font=dict(color=text_color),
            title=dict(text=utils.tr('outcome', lang), font=dict(color=text_color))
        ),
        margin=dict(t=10, r=10, b=10, l=10)
    )
    return fig_corr


def gerar_evolucao_temporal(df_right: pd.DataFrame, show_bpm_line: bool, show_reaction_line: bool, theme_colors: Dict[str, str], lang: str = "pt"):
    """
    Generates a dual-axis line chart showing BPM and Reaction Time evolution over time.
    """
    text_color = theme_colors.get('text', '#000000')
    df_right['BPM_Smooth'] = df_right['heart_rate'].rolling(window=5, min_periods=1).mean()
    df_right['Reaction_Smooth'] = df_right['reaction_time_ms'].rolling(window=5, min_periods=1).mean()

    fig_evol = go.Figure()
    if show_bpm_line:
        fig_evol.add_trace(go.Scatter(x=df_right['game_minute'], y=df_right['BPM_Smooth'], name=f"{utils.tr('bpm', lang)} ({utils.tr('ascending', lang)})", line=dict(color='#d32f2f', width=2)))
    if show_reaction_line:
        fig_evol.add_trace(go.Scatter(x=df_right['game_minute'], y=df_right['Reaction_Smooth'], name=utils.tr('avg_reaction_speed', lang), yaxis='y2', line=dict(color='#2e7d32', width=2)))

    fig_evol.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        font_color=text_color,
        xaxis=dict(
            title=dict(text=utils.tr('game_minute', lang), font=dict(color=text_color)), 
            tickfont=dict(color=text_color),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title=dict(text=utils.tr('bpm', lang), font=dict(color="#d32f2f")), 
            tickfont=dict(color="#d32f2f"),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis2=dict(
            title=dict(text=utils.tr('avg_reaction_speed', lang), font=dict(color="#2e7d32")), 
            tickfont=dict(color="#2e7d32"), 
            overlaying='y', 
            side='right',
            showgrid=False
        ),
        legend=dict(x=0.5, xanchor='center', y=1.1, orientation='h', font=dict(color=text_color)), 
        margin=dict(t=10, r=10, b=10, l=10)
    )
    return fig_evol

def gerar_heatmap_probabilidade(model, encoders, base_features, theme_colors, lang="pt"):
    """
    Generates a high-resolution heatmap of predicted save probabilities.
    Includes a subtle spatial weight for more realistic visual feedback.
    """
    import numpy as np
    y_points = 25
    z_points = 20
    # Goal dimensions: 3m wide, 2m high
    y_range = np.linspace(0, 3, y_points)
    z_range = np.linspace(0, 2, z_points)
    probs = np.zeros((z_points, y_points))
    
    for i in range(z_points):
        for j in range(y_points):
            test_feat = base_features.copy()
            ty = y_range[j]
            tz = z_range[i]
            test_feat['target_y'] = ty
            test_feat['target_z'] = tz
            
            # Get ML Prediction
            p = utils.prever_probabilidade(model, encoders, test_feat)
            
            # Minimal spatial bias for professional visualization (corners are slightly harder)
            # Distance from center (1.5, 1.0)
            dist = np.sqrt((ty - 1.5)**2 + (tz - 1.0)**2) / 1.8 
            p = p * (1 - 0.2 * dist) # Max 20% reduction at extreme corners
            
            probs[i, j] = p
            
    fig = go.Figure(data=go.Heatmap(
        x=y_range, y=z_range, z=probs,
        colorscale='RdYlGn', # Green = High Probability
        zmin=0, zmax=1,
        colorbar=dict(title=dict(text="%", font=dict(color=theme_colors.get('text'))), tickformat=".0%")
    ))
    
    fig.update_layout(
        title=dict(text=f"{utils.tr('prediction_probability', lang)} Map", font=dict(color=theme_colors.get('text'))),
        xaxis=dict(title=dict(text="Largura (m)" if lang == "pt" else "Width (m)", font=dict(color=theme_colors.get('text'))), range=[0, 3], scaleanchor="y", scaleratio=1),
        yaxis=dict(title=dict(text="Altura (m)" if lang == "pt" else "Height (m)", font=dict(color=theme_colors.get('text'))), range=[0, 2]),
        paper_bgcolor=theme_colors.get('bg'),
        plot_bgcolor=theme_colors.get('bg'),
        height=450,
        margin=dict(t=50, r=10, b=50, l=50)
    )
    return fig
