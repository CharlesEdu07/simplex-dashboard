from scipy.optimize import linprog
import pandas as pd


def calcular_otimizacao(df, tempo_total_disponivel):
    tempo_minimo_obrigatorio = (df["minimo"] * df["tempo"]).sum()

    if tempo_minimo_obrigatorio > tempo_total_disponivel:
        deficit = tempo_minimo_obrigatorio - tempo_total_disponivel
        msg_erro = (
            f"INVIÁVEL: Os mínimos exigem {tempo_minimo_obrigatorio:.1f}h, "
            f"mas você só tem {tempo_total_disponivel}h. "
            f"Faltam {deficit:.1f}h."
        )
        return None, msg_erro

    c = -df["lucro_unitario"].values
    A = [df["tempo"].values]
    b = [tempo_total_disponivel]
    bounds = list(zip(df["minimo"], df["maximo"]))

    resultado = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

    if not resultado.success:
        return None, f"Erro matemático: {resultado.message}"

    df["qtd_sugerida"] = resultado.x.round(0)

    df["lucro_meta"] = df["qtd_sugerida"] * df["lucro_unitario"]
    df["faturamento_meta"] = df["qtd_sugerida"] * df["venda"]
    df["tempo_meta"] = df["qtd_sugerida"] * df["tempo"]

    if "quantidade_real" in df.columns:
        df["lucro_real"] = df["quantidade_real"] * df["lucro_unitario"]
        df["faturamento_real"] = df["quantidade_real"] * df["venda"]
        df["tempo_real"] = df["quantidade_real"] * df["tempo"]

        df["desvio_qtd"] = df["quantidade_real"] - df["qtd_sugerida"]
        df["desvio_lucro"] = df["lucro_real"] - df["lucro_meta"]
    else:
        cols = [
            "lucro_real",
            "faturamento_real",
            "tempo_real",
            "desvio_qtd",
            "desvio_lucro",
        ]
        for col in cols:
            df[col] = 0.0

    return df.sort_values(by="rentabilidade_hora", ascending=False), None
