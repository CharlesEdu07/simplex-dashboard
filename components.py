from dash import dcc, html, dash_table
import plotly.graph_objects as go
import pandas as pd
from dash.dash_table.Format import Format, Group

COLORS = {
    "background": "#0f172a",
    "card_bg": "#1e293b",
    "text": "#ffffff",
    "blue": "#3b82f6",
    "green": "#10b981",
    "red": "#ef4444",
    "purple": "#8b5cf6",
    "yellow": "#f59e0b",
    "gray": "#64748b",
}


def card_metrica(
    titulo,
    valor_principal,
    explicacao,
    cor_titulo,
    valor_secundario=None,
    is_moeda=True,
):
    valor_fmt = (
        f"R$ {valor_principal:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
        if is_moeda
        else valor_principal
    )

    if valor_secundario is not None:
        delta = valor_principal - valor_secundario
        cor_delta = COLORS["green"] if delta >= 0 else COLORS["red"]
        sinal = "+" if delta >= 0 else ""
        delta_txt = (
            f"{sinal}R$ {abs(delta):,.0f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
            if is_moeda
            else f"{sinal}{delta:+.1f}"
        )
        secundario = html.Div(
            [
                html.Span(
                    "vs Meta → ", style={"color": COLORS["gray"], "fontSize": "13px"}
                ),
                html.Span(delta_txt, style={"color": cor_delta, "fontWeight": "bold"}),
            ]
        )
    else:
        secundario = html.Span(
            explicacao, style={"color": COLORS["gray"], "fontSize": "13px"}
        )

    return html.Div(
        [
            html.Div(
                titulo,
                style={
                    "color": cor_titulo,
                    "fontSize": "15px",
                    "fontWeight": "bold",
                    "marginBottom": "8px",
                },
            ),
            html.Div(
                valor_fmt,
                style={"color": "white", "fontSize": "28px", "fontWeight": "bold"},
            ),
            secundario,
        ],
        style={
            "backgroundColor": COLORS["card_bg"],
            "padding": "20px",
            "borderRadius": "12px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.3)",
            "flex": "1",
            "minWidth": "220px",
            "margin": "8px",
        },
    )


def grafico_distribuicao_tempo(df):
    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["servico"],
                values=df["tempo_meta"],
                hole=0.5,
                textinfo="label+percent",
                hoverinfo="label+value+percent",
                marker=dict(
                    colors=[
                        "#3b82f6",
                        "#8b5cf6",
                        "#10b981",
                        "#f59e0b",
                        "#ef4444",
                        "#06b6d4",
                    ]
                ),
            )
        ]
    )

    fig.update_layout(
        title={
            "text": "Para onde vai o seu tempo este mês?",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": "white"},
        },
        annotations=[
            dict(
                text="Distribuição<br>do Tempo",
                x=0.5,
                y=0.5,
                font_size=14,
                showarrow=False,
            )
        ],
        paper_bgcolor=COLORS["card_bg"],
        plot_bgcolor=COLORS["card_bg"],
        font={"color": COLORS["text"]},
        legend={"font": {"size": 11}},
    )
    return html.Div(
        [
            html.Div(
                "Mostra quanto tempo você vai gastar em cada serviço. "
                "Quanto maior a fatia, mais tempo esse serviço consome.",
                style={
                    "color": COLORS["gray"],
                    "fontSize": "13px",
                    "marginBottom": "10px",
                },
            ),
            dcc.Graph(figure=fig, config={"displayModeBar": False}),
        ],
        style={
            "backgroundColor": COLORS["card_bg"],
            "padding": "15px",
            "borderRadius": "12px",
            "margin": "10px 0",
        },
    )


def grafico_rentabilidade_pareto(df):
    df_sorted = df.sort_values("lucro_meta", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=df_sorted["lucro_meta"],
            y=df_sorted["servico"],
            orientation="h",
            marker_color=COLORS["purple"],
            text=[
                f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                for v in df_sorted["lucro_meta"]
            ],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Lucro esperado: R$ %{x:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title={
            "text": "Quais serviços mais pagam o seu bolso?",
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="Lucro Esperado (R$)",
        paper_bgcolor=COLORS["card_bg"],
        plot_bgcolor=COLORS["card_bg"],
        font={"color": COLORS["text"]},
        height=400 + len(df) * 15,
    )

    return html.Div(
        [
            html.Div(
                "Os serviços no topo são os que mais geram lucro. "
                "Foque neles para ganhar mais com o mesmo tempo!",
                style={
                    "color": COLORS["yellow"],
                    "fontSize": "13px",
                    "fontWeight": "bold",
                    "marginBottom": "10px",
                },
            ),
            dcc.Graph(figure=fig, config={"displayModeBar": False}),
        ],
        style={
            "backgroundColor": COLORS["card_bg"],
            "padding": "15px",
            "borderRadius": "12px",
            "margin": "10px 0",
        },
    )


def grafico_comparativo_financeiro(df):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Faturamento Previsto",
            x=df["servico"],
            y=df["faturamento_meta"],
            marker_color=COLORS["blue"],
        )
    )
    fig.add_trace(
        go.Bar(
            name="Faturamento Real",
            x=df["servico"],
            y=df["faturamento_real"],
            marker_color=COLORS["green"],
        )
    )
    fig.add_trace(
        go.Bar(
            name="Custo Real (mão de obra + material)",
            x=df["servico"],
            y=df["quantidade_real"] * df["custo"],
            marker_color=COLORS["red"],
        )
    )

    fig.update_layout(
        barmode="group",
        title="O que você planejou × O que realmente aconteceu",
        paper_bgcolor=COLORS["card_bg"],
        plot_bgcolor=COLORS["card_bg"],
        font={"color": COLORS["text"]},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        height=500,
    )

    return html.Div(
        [
            html.Div(
                "Compare o que você deveria faturar com o que de fato faturou. "
                "Verde = bom, vermelho = gastou demais.",
                style={
                    "color": COLORS["gray"],
                    "fontSize": "13px",
                    "marginBottom": "10px",
                },
            ),
            dcc.Graph(figure=fig),
        ],
        style={
            "backgroundColor": COLORS["card_bg"],
            "padding": "15px",
            "borderRadius": "12px",
            "margin": "10px 0",
        },
    )


def grafico_waterfall_financeiro(df):
    valores = df["desvio_lucro"].tolist()
    servicos = df["servico"].tolist()

    medida = ["relative"] * len(valores) + ["total"]
    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=medida,
            x=servicos + ["TOTAL"],
            textposition="outside",
            text=[f"R$ {abs(v):,.0f}{' (perda)' if v<0 else ''}" for v in valores]
            + [f"R$ {sum(valores):,.0f}"],
            y=valores + [sum(valores)],
            connector={"line": {"color": "white"}},
            increasing={"marker": {"color": COLORS["green"]}},
            decreasing={"marker": {"color": COLORS["red"]}},
            totals={"marker": {"color": COLORS["purple"]}},
        )
    )

    fig.update_layout(
        title="Onde você ganhou ou perdeu dinheiro este mês?",
        paper_bgcolor=COLORS["card_bg"],
        plot_bgcolor=COLORS["card_bg"],
        font={"color": COLORS["text"]},
        height=500,
    )

    return html.Div(
        [
            html.Div(
                "Barras verdes = ganhou mais que o planejado. "
                "Barras vermelhas = perdeu dinheiro nesse serviço.",
                style={
                    "color": COLORS["gray"],
                    "fontSize": "13px",
                    "marginBottom": "10px",
                },
            ),
            dcc.Graph(figure=fig),
        ],
        style={
            "backgroundColor": COLORS["card_bg"],
            "padding": "15px",
            "borderRadius": "12px",
            "margin": "10px 0",
        },
    )


def grafico_gauge(real, meta, titulo, prefix):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=real,
            number={"prefix": prefix, "valueformat": ",.0f"},
            delta={"reference": meta},
            gauge={
                "axis": {"range": [0, meta * 1.4]},
                "bar": {"color": COLORS["purple"]},
                "steps": [
                    {"range": [0, meta * 0.8], "color": "#ef4444"},  # vermelho sólido
                    {"range": [meta * 0.8, meta], "color": "#f59e0b"},  # amarelo sólido
                    {"range": [meta, meta * 1.4], "color": "#10b981"},  # verde sólido
                ],
                "threshold": {"line": {"color": "white", "width": 6}, "value": meta},
            },
            title={"text": titulo},
        )
    )
    fig.update_layout(
        paper_bgcolor=COLORS["card_bg"], font={"color": "white"}, height=300
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def gauges_por_servico(df):
    gauges = []

    for _, row in df.iterrows():
        servico = row["servico"]
        realizado = float(row["quantidade_real"] or 0)
        meta = max(float(row["qtd_sugerida"]), 1)
        percentual = min((realizado / meta) * 100, 150)

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=percentual,
                number={"suffix": "%", "font": {"size": 32, "color": "white"}},
                delta={"reference": 100, "relative": False, "position": "top"},
                title={
                    "text": f"<b>{servico}</b><br>{int(realizado)} de {int(meta)}",
                    "font": {"size": 16},
                },
                gauge={
                    "axis": {
                        "range": [0, 120],
                        "tickvals": [0, 70, 100, 120],
                        "ticktext": ["0%", "70%", "100%", "120%"],
                        "tickcolor": "white",
                    },
                    "bar": {"color": "white", "thickness": 0.3},
                    "bgcolor": "#1e293b",
                    "steps": [
                        {
                            "range": [0, 70],
                            "color": "rgba(239, 68, 68, 0.3)",
                        },  # vermelho suave
                        {
                            "range": [70, 100],
                            "color": "rgba(245, 158, 11, 0.4)",
                        },  # amarelo suave
                        {
                            "range": [100, 120],
                            "color": "rgba(16, 185, 129, 0.5)",
                        },  # verde suave
                    ],
                    "threshold": {
                        "line": {"color": "white", "width": 8},
                        "thickness": 1,
                        "value": 100,
                    },
                },
            )
        )

        fig.update_layout(
            height=300,
            margin=dict(l=30, r=30, t=70, b=20),
            paper_bgcolor=COLORS["card_bg"],
            font={"color": "white"},
        )

        gauges.append(
            html.Div(
                dcc.Graph(figure=fig, config={"displayModeBar": False}),
                style={
                    "width": "340px",
                    "margin": "20px",
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
            )
        )

    return html.Div(
        [
            html.H2(
                "Desempenho por serviço – Você está cumprindo as metas?",
                style={
                    "textAlign": "center",
                    "color": COLORS["blue"],
                    "margin": "60px 0 30px",
                    "fontSize": "28px",
                    "fontWeight": "bold",
                },
            ),
            html.Div(gauges, style={"textAlign": "center", "padding": "20px"}),
        ]
    )


def tabela_detalhada(df):
    df_vis = df[
        [
            "servico",
            "qtd_sugerida",
            "quantidade_real",
            "lucro_meta",
            "lucro_real",
            "desvio_lucro",
        ]
    ].copy()
    df_vis.columns = [
        "Serviço",
        "Qtd Ideal",
        "Qtd Feita",
        "Lucro Ideal",
        "Lucro Real",
        "Diferença",
    ]

    df_vis["Qtd Ideal"] = df_vis["Qtd Ideal"].round(0).astype(int)
    df_vis["Qtd Feita"] = df_vis["Qtd Feita"].fillna(0).round(0).astype(int)

    def formatar_moeda(valor):
        if pd.isna(valor):
            return "R$ 0"
        valor = float(valor)
        return f"R$ {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    df_vis["Lucro Ideal"] = df_vis["Lucro Ideal"].apply(formatar_moeda)
    df_vis["Lucro Real"] = df_vis["Lucro Real"].apply(formatar_moeda)
    df_vis["Diferença"] = df_vis["Diferença"].apply(
        lambda x: (
            f"+{formatar_moeda(abs(x))}"
            if x >= 0
            else f"-{formatar_moeda(abs(x))}".replace("R$ +", "R$ ").replace(
                "R$ -", "-R$ "
            )
        )
    )

    return html.Div(
        [
            html.H3(
                "O que você deveria fazer × O que você fez",
                style={"color": "white", "marginBottom": "15px"},
            ),
            html.P(
                "Siga a coluna 'Qtd Ideal' para bater a meta de lucro máximo!",
                style={
                    "color": COLORS["yellow"],
                    "fontSize": "15px",
                    "fontWeight": "bold",
                    "marginBottom": "20px",
                },
            ),
            dash_table.DataTable(
                data=df_vis.to_dict("records"),
                columns=[
                    {"name": "Serviço", "id": "Serviço"},
                    {"name": "Qtd Ideal", "id": "Qtd Ideal"},
                    {"name": "Qtd Feita", "id": "Qtd Feita"},
                    {"name": "Lucro Ideal", "id": "Lucro Ideal"},
                    {"name": "Lucro Real", "id": "Lucro Real"},
                    {"name": "Diferença", "id": "Diferença"},
                ],
                style_header={
                    "backgroundColor": "#334155",
                    "color": "white",
                    "fontWeight": "bold",
                    "textAlign": "center",
                },
                style_cell={
                    "textAlign": "center",
                    "backgroundColor": COLORS["card_bg"],
                    "color": "white",
                    "padding": "12px",
                    "fontSize": "14px",
                },
                style_data_conditional=[
                    {
                        "if": {
                            "column_id": "Diferença",
                            "filter_query": '{Diferença} contains "-"',
                        },
                        "color": COLORS["red"],
                        "fontWeight": "bold",
                    },
                    {
                        "if": {
                            "column_id": "Diferença",
                            "filter_query": '{Diferença} contains "+"',
                        },
                        "color": COLORS["green"],
                        "fontWeight": "bold",
                    },
                    {
                        "if": {"column_id": "Qtd Ideal"},
                        "backgroundColor": "#1e40af",
                        "color": "white",
                        "fontWeight": "bold",
                        "fontSize": "16px",
                    },
                ],
                style_table={"overflowX": "auto"},
                page_size=15,
            ),
        ],
        style={
            "backgroundColor": COLORS["card_bg"],
            "padding": "25px",
            "borderRadius": "12px",
            "marginTop": "30px",
            "boxShadow": "0 4px 20px rgba(0,0,0,0.3)",
        },
    )


def upload_area(id_componente, texto_label):
    return dcc.Upload(
        id=id_componente,
        children=html.Div(
            [
                html.Div(
                    [
                        html.Span(
                            "Arraste ou clique para carregar",
                            style={"fontSize": "13px", "color": "#94a3b8"},
                        ),
                        html.Br(),
                        html.Span(
                            texto_label,
                            style={
                                "fontSize": "17px",
                                "color": "white",
                                "fontWeight": "bold",
                            },
                        ),
                    ],
                    style={"textAlign": "center"},
                )
            ],
            style={"padding": "20px"},
        ),
        style={
            "width": "100%",
            "height": "130px",
            "lineHeight": "60px",
            "borderWidth": "3px",
            "borderStyle": "dashed",
            "borderRadius": "12px",
            "borderColor": "#475569",
            "backgroundColor": "#1e293b",
            "textAlign": "center",
            "margin": "15px 0",
            "cursor": "pointer",
        },
        style_active={"borderColor": COLORS["blue"], "borderStyle": "solid"},
        style_reject={"borderColor": COLORS["red"]},
        multiple=False,
    )
