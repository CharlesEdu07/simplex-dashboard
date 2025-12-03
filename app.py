import dash
from dash import html, dcc, Input, Output, State
import webbrowser
from threading import Timer

import data_manager
import optimizer
import components

app = dash.Dash(__name__, suppress_callback_exceptions=True)

COLORS = components.COLORS

app.layout = html.Div(
    [
        html.Div(
            [
                html.H2(
                    "Configuração", style={"color": "white", "marginBottom": "20px"}
                ),
                html.Label(
                    "1. Template de metas (Obrigatório)", style={"color": "#94a3b8"}
                ),
                components.upload_area("upload-template", "Carregar template"),
                html.Div(
                    id="output-nome-template",
                    style={
                        "color": COLORS["green"],
                        "fontSize": "12px",
                        "marginBottom": "15px",
                    },
                ),
                html.Label(
                    "2. Dados realizados (Opcional)", style={"color": "#94a3b8"}
                ),
                components.upload_area("upload-realizado", "Carregar mês atual"),
                html.Div(
                    id="output-nome-realizado",
                    style={
                        "color": COLORS["green"],
                        "fontSize": "12px",
                        "marginBottom": "15px",
                    },
                ),
                html.Label("Horas disponíveis no mês", style={"color": "#94a3b8"}),
                dcc.Input(
                    id="input-tempo",
                    type="number",
                    value=360,
                    min=1,
                    style={
                        "width": "100%",
                        "padding": "10px",
                        "borderRadius": "5px",
                        "border": "none",
                        "backgroundColor": "#334155",
                        "color": "white",
                    },
                ),
                html.Button(
                    "CALCULAR OTIMIZAÇÃO",
                    id="btn-calcular",
                    n_clicks=0,
                    style={
                        "width": "100%",
                        "padding": "15px",
                        "backgroundColor": COLORS["blue"],
                        "color": "white",
                        "border": "none",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "fontWeight": "bold",
                        "marginTop": "20px",
                    },
                ),
            ],
            style={
                "width": "280px",
                "padding": "30px",
                "backgroundColor": "#1e293b",
                "borderRight": "1px solid #334155",
                "position": "fixed",
                "height": "100%",
                "overflowY": "auto",
                "boxShadow": "2px 0 10px rgba(0,0,0,0.3)",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "Dashboard",
                            style={"color": "white", "fontSize": "28px"},
                        ),
                        html.P(
                            "Carregue os arquivos ao lado e clique em calcular para ver onde você ganha mais dinheiro.",
                            style={"color": "#94a3b8", "fontSize": "16px"},
                        ),
                    ],
                    style={"textAlign": "center", "marginBottom": "40px"},
                ),
                dcc.Loading(
                    id="loading-1",
                    type="cube",
                    color=components.COLORS["blue"],
                    children=html.Div(id="dashboard-content"),
                ),
            ],
            style={"marginLeft": "320px", "padding": "40px", "minHeight": "100vh"},
        ),
    ],
    style={
        "backgroundColor": components.COLORS["background"],
        "fontFamily": "Segoe UI, sans-serif",
    },
)


@app.callback(
    Output("output-nome-template", "children"), Input("upload-template", "filename")
)
def update_nome_template(filename):
    return f"Template: {filename}" if filename else "Nenhum arquivo carregado"


@app.callback(
    Output("output-nome-realizado", "children"), Input("upload-realizado", "filename")
)
def update_nome_realizado(filename):
    return f"Realizado: {filename}" if filename else "Opcional – não carregado"


@app.callback(
    Output("dashboard-content", "children"),
    Input("btn-calcular", "n_clicks"),
    State("upload-template", "contents"),
    State("upload-template", "filename"),
    State("upload-realizado", "contents"),
    State("upload-realizado", "filename"),
    State("input-tempo", "value"),
    prevent_initial_call=True,
)
def update_dashboard(n_clicks, cont_temp, name_temp, cont_real, name_real, tempo_disp):
    if not cont_temp:
        return html.Div(
            "Carregue o Template para começar",
            style={
                "color": COLORS["yellow"],
                "textAlign": "center",
                "fontSize": "20px",
                "marginTop": "100px",
            },
        )

    try:
        df_template = data_manager.parse_upload(cont_temp, name_temp)

        if df_template is None:
            return html.Div("Erro ao ler o Template", style={"color": COLORS["red"]})

        df_realizado = None

        if cont_real:
            df_realizado = data_manager.parse_upload(cont_real, name_real)

        df_raw = data_manager.consolidar_dados(df_template, df_realizado)
        df_final, erro_opt = optimizer.calcular_otimizacao(df_raw, tempo_disp or 360)

        if erro_opt:
            return html.Div(
                [
                    html.H3("Impossível otimizar", style={"color": COLORS["yellow"]}),
                    html.P(erro_opt, style={"color": "white", "fontSize": "20px"}),
                    html.P(
                        "Aumente as horas ou diminua os mínimos obrigatórios",
                        style={"color": COLORS["gray"]},
                    ),
                ],
                style={"textAlign": "center", "marginTop": "80px"},
            )

        meta_lucro = df_final["lucro_meta"].sum()
        meta_faturamento = df_final["faturamento_meta"].sum()
        meta_tempo = df_final["tempo_meta"].sum()

        real_lucro = df_final["lucro_real"].sum()
        real_faturamento = df_final["faturamento_real"].sum()
        real_tempo = df_final["tempo_real"].sum()

        tem_real = real_tempo > 0.1
        gauges_servicos = (
            components.gauges_por_servico(df_final) if tem_real else html.Div()
        )

        if tem_real:
            kpi_topo = html.Div(
                [
                    components.grafico_gauge(
                        real_lucro, meta_lucro, "Lucro real vs Meta", "R$ "
                    ),
                    components.grafico_gauge(
                        real_faturamento,
                        meta_faturamento,
                        "Faturamento real vs Previsto",
                        "R$ ",
                    ),
                    components.grafico_gauge(
                        real_tempo, meta_tempo, "Tempo real vs Planejado", ""
                    ),
                ],
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "30px",
                    "justifyContent": "center",
                    "margin": "30px 0",
                },
            )
        else:
            kpi_topo = html.Div(
                [
                    components.card_metrica(
                        "LUCRO MÁXIMO POSSÍVEL",
                        meta_lucro,
                        "Se seguir o plano abaixo",
                        COLORS["green"],
                        is_moeda=True,
                    ),
                    components.card_metrica(
                        "FATURAMENTO ESPERADO",
                        meta_faturamento,
                        "Valor total que entra no caixa",
                        COLORS["blue"],
                        is_moeda=True,
                    ),
                    components.card_metrica(
                        "TEMPO PLANEJADO",
                        f"{meta_tempo:.0f}h",
                        f"de {tempo_disp}h disponíveis",
                        COLORS["purple"],
                        is_moeda=False,
                    ),
                    components.card_metrica(
                        "VALOR DA SUA HORA",
                        f"R$ {meta_lucro/meta_tempo:.0f}",
                        "Esse é o quanto vale cada hora otimizada!",
                        COLORS["yellow"],
                        is_moeda=False,
                    ),
                ],
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "20px",
                    "justifyContent": "center",
                    "margin": "30px 0",
                },
            )

        if tem_real:
            graficos = html.Div(
                [
                    html.Div(
                        components.grafico_comparativo_financeiro(df_final),
                        style={"flex": "1", "minWidth": "500px"},
                    ),
                    html.Div(
                        components.grafico_waterfall_financeiro(df_final),
                        style={"flex": "1", "minWidth": "500px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "30px",
                    "margin": "40px 0",
                },
            )
        else:
            graficos = html.Div(
                [
                    html.Div(
                        components.grafico_rentabilidade_pareto(df_final),
                        style={"flex": "1", "minWidth": "500px"},
                    ),
                    html.Div(
                        components.grafico_distribuicao_tempo(df_final),
                        style={"flex": "1", "minWidth": "400px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "30px",
                    "margin": "40px 0",
                },
            )

        return html.Div(
            [
                html.H1(
                    "Seu resultado está pronto!",
                    style={
                        "textAlign": "center",
                        "color": COLORS["blue"],
                        "margin": "20px 0",
                        "fontSize": "32px",
                    },
                ),
                kpi_topo,
                graficos,
                gauges_servicos,
                components.tabela_detalhada(df_final),
            ],
            style={"padding": "20px"},
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return html.Div(
            f"Erro: {str(e)}", style={"color": COLORS["red"], "textAlign": "center"}
        )


if __name__ == "__main__":
    Timer(1, lambda: webbrowser.open("http://127.0.0.1:8050")).start()

    print("Dashboard rodando em http://127.0.0.1:8050")

    app.run(debug=False, port=8050)
