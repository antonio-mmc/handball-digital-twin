"""
Visualization engine for the Digital Twin Goalkeeper Dashboard.
Uses Plotly for interactive chart generation.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from PIL import Image

def gerar_figura_baliza(df_golos, n_detalhe, n_opacidade, mostrar_bolas, img_path, theme_colors):
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
            text=df_golos.apply(lambda row: f"Golo ({row['game_minute']} min)<br>Shooter: {row['shooter_role']}", axis=1),
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


def gerar_grelha_3x3(df_grid, theme_colors):
    """
    Generates a 3x3 text-based grid showing save rates for goal sectors.
    """
    # Create the coordinate zones for Y and Z axes
    df_grid['y_zone'] = pd.cut(df_grid['target_y'], bins=[0, 1, 2, 3.01], labels=['Esquerda', 'Centro', 'Direita'], include_lowest=True)
    df_grid['z_zone'] = pd.cut(df_grid['target_z'], bins=[0, 0.67, 1.33, 2.01], labels=['Base', 'Meio', 'Topo'], include_lowest=True)

    grid_stats = df_grid.groupby(['z_zone', 'y_zone'], observed=False).apply(
        lambda x: pd.Series({
            'Sucesso': len(x[x['outcome'].isin(['SAVE', 'MISS'])]), 
            'TotalPosicao': len(x)
        })
    ).reset_index()

    grid_stats['TaxaSucesso'] = grid_stats.apply(
        lambda row: (row['Sucesso'] / row['TotalPosicao'] * 100) if row['TotalPosicao'] > 0 else 0, 
        axis=1
    )

    text_matrix = grid_stats.pivot(index='z_zone', columns='y_zone', values='TaxaSucesso').fillna(0)
    success_matrix = grid_stats.pivot(index='z_zone', columns='y_zone', values='Sucesso').fillna(0)
    totals_matrix = grid_stats.pivot(index='z_zone', columns='y_zone', values='TotalPosicao').fillna(0)

    y_labels = ['Esquerda', 'Centro', 'Direita']
    z_labels = ['Base', 'Meio', 'Topo']
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


def gerar_barras_posicao(df_role_stats, asc_order, theme_colors):
    """
    Generates a horizontal bar chart for efficiency by shooter role.
    """
    text_color = theme_colors.get('text', '#000000')
    fig = px.bar(df_role_stats, x='Eficacia', y='shooter_role', orientation='h',
                 color='Eficacia', color_continuous_scale='RdYlGn',
                 labels={'shooter_role': 'Posição', 'Eficacia': 'Taxa de Defesa (%)'})
    
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
        xaxis=dict(title=dict(text="Taxa de Defesa (%)", font=dict(color=text_color)), 
                   range=[0, 135], showgrid=True, gridcolor='rgba(128,128,128,0.2)', tickfont=dict(color=text_color)),
        yaxis=dict(title=dict(text="Posição", font=dict(color=text_color)), tickfont=dict(color=text_color)),
        coloraxis_colorbar=dict(title=dict(text=" (%)", font=dict(color=text_color)), tickfont=dict(color=text_color)),
        height=450, margin=dict(t=10, r=20, b=10, l=10)
    )
    return fig


def gerar_matriz_eficacia(df_temp, sel_eficacia, theme_colors):
    """
    Generates an interactive heatmap matrix (Shot Type vs. Game Sequence).
    """
    matrix_data = df_temp.groupby(['shot_type', 'game_seq']).apply(
        lambda x: (len(x[x['outcome'] == 'SAVE']) / len(x) * 100) if len(x) > 0 else None
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
            title=dict(text="Eficácia (%)", font=dict(color=text_color)),
            thickness=15,
            tickfont=dict(color=text_color)
        )
    ))

    fig_matrix.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        font_color=text_color,
        xaxis=dict(
            title=dict(text="Sequência de Jogos", font=dict(color=text_color)),
            tickfont=dict(color=text_color),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title=dict(text="Tipo de Remate", font=dict(color=text_color)),
            tickfont=dict(color=text_color),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        height=400,
        margin=dict(t=10, r=20, b=10, l=10)
    )
    return fig_matrix


def gerar_ranking_eficacia(df_eff, asc_eff, theme_colors):
    """
    Generates a vertical bar chart ranking efficiency by shot type.
    """
    text_color = theme_colors.get('text', '#000000')
    max_eficacia = df_eff['Eficacia'].max()
    y_max_eff = max(105, max_eficacia * 1.15)
    
    fig_eff = px.bar(
        df_eff, x='shot_type', y='Eficacia',
        color='Eficacia', color_continuous_scale='Blues',
        text=df_eff['Eficacia'].apply(lambda x: f"{x:.0f}%")
    )
    fig_eff.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        font_color=text_color,
        xaxis=dict(title=dict(text="Tipo de Remate", font=dict(color=text_color)), tickfont=dict(color=text_color)),
        yaxis=dict(
            title=dict(text="% Eficácia", font=dict(color=text_color)), 
            range=[0, y_max_eff], 
            tickfont=dict(color=text_color),
            gridcolor='rgba(128,128,128,0.2)'
        ),
        showlegend=False,
        coloraxis_showscale=False, margin=dict(t=10, r=10, b=10, l=10)
    )
    fig_eff.update_traces(textposition='outside', textfont=dict(color=text_color, size=12, weight='bold'))
    return fig_eff


def gerar_ranking_reacao(df_react, asc_react, theme_colors):
    """
    Generates a vertical bar chart ranking reaction time by shot type.
    """
    text_color = theme_colors.get('text', '#000000')
    max_reacao = df_react['Reacao_Media'].max()
    y_max_react = max(520, max_reacao * 1.15)
    
    fig_react = px.bar(
        df_react, x='shot_type', y='Reacao_Media',
        color='Reacao_Media', color_continuous_scale='Viridis',
        text=df_react['Reacao_Media'].apply(lambda x: f"{x:.0f} ms")
    )
    fig_react.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'), 
        font_color=text_color,
        xaxis=dict(title=dict(text="Tipo de Remate", font=dict(color=text_color)), tickfont=dict(color=text_color)),
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


def gerar_scatter_correlacao(df_left, theme_colors):
    """
    Generates a scatter plot showing the correlation between Heart Rate and Reaction Time.
    """
    text_color = theme_colors.get('text', '#000000')
    fig_corr = px.scatter(
        df_left,
        x='heart_rate',
        y='reaction_time_ms',
        color='outcome',
        color_discrete_map={'GOAL': '#ff4b4b', 'SAVE': '#2e7d32', 'MISS': 'gray'},
        hover_data=['game_minute', 'shooter_role', 'shot_type'],
        labels={'heart_rate': 'Batimento Cardíaco (BPM)', 'reaction_time_ms': 'Tempo de Reação (ms)'}
    )
    fig_corr.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        font_color=text_color,
        xaxis=dict(title=dict(font=dict(color=text_color)), tickfont=dict(color=text_color), gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(title=dict(font=dict(color=text_color)), tickfont=dict(color=text_color), gridcolor='rgba(128,128,128,0.2)'),
        legend=dict(
            font=dict(color=text_color),
            title=dict(text='Outcome', font=dict(color=text_color))
        ),
        margin=dict(t=10, r=10, b=10, l=10)
    )
    return fig_corr


def gerar_evolucao_temporal(df_right, show_bpm_line, show_reaction_line, theme_colors):
    """
    Generates a dual-axis line chart showing BPM and Reaction Time evolution over time.
    """
    text_color = theme_colors.get('text', '#000000')
    df_right['BPM_Smooth'] = df_right['heart_rate'].rolling(window=5, min_periods=1).mean()
    df_right['Reaction_Smooth'] = df_right['reaction_time_ms'].rolling(window=5, min_periods=1).mean()

    fig_evol = go.Figure()
    if show_bpm_line:
        fig_evol.add_trace(go.Scatter(x=df_right['game_minute'], y=df_right['BPM_Smooth'], name='BPM (Média)', line=dict(color='#d32f2f', width=2)))
    if show_reaction_line:
        fig_evol.add_trace(go.Scatter(x=df_right['game_minute'], y=df_right['Reaction_Smooth'], name='Reação (ms)', yaxis='y2', line=dict(color='#2e7d32', width=2)))

    fig_evol.update_layout(
        plot_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        paper_bgcolor=theme_colors.get('bg', '#f0f2f6'),
        font_color=text_color,
        xaxis=dict(
            title=dict(text="Minuto de Jogo", font=dict(color=text_color)), 
            tickfont=dict(color=text_color),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            title=dict(text="BPM", font=dict(color="#d32f2f")), 
            tickfont=dict(color="#d32f2f"),
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis2=dict(
            title=dict(text="Reação (ms)", font=dict(color="#2e7d32")), 
            tickfont=dict(color="#2e7d32"), 
            overlaying='y', 
            side='right',
            showgrid=False
        ),
        legend=dict(x=0.5, xanchor='center', y=1.1, orientation='h', font=dict(color=text_color)), 
        margin=dict(t=10, r=10, b=10, l=10)
    )
    return fig_evol
