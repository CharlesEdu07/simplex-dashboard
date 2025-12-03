import base64
import io
import pandas as pd


def parse_upload(contents, filename):
    if contents is None:
        return None

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        if "csv" in filename.lower():
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), sep=",", decimal=",")
        elif "xlsx" in filename.lower():
            df = pd.read_excel(io.BytesIO(decoded), engine="openpyxl")
        elif "xls" in filename.lower():
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None
    except Exception as e:
        print(f"ERRO DE LEITURA ({filename}): {e}")
        return None

    return df


def limpar_dados_numericos(df, colunas):
    for col in colunas:
        if col in df.columns:
            df[col] = df[col].astype(str)

            df[col] = df[col].str.replace("R$", "", regex=False)
            df[col] = df[col].str.replace(" ", "", regex=False)

            df[col] = df[col].str.replace(",", ".", regex=False)

            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def consolidar_dados(df_template, df_realizado=None):
    cols_obrigat = ["servico", "tempo", "custo", "venda", "minimo", "maximo"]

    df_template.columns = df_template.columns.str.lower().str.strip()

    missing = [c for c in cols_obrigat if c not in df_template.columns]
    if missing:
        raise ValueError(f"Faltam colunas no Template: {missing}")

    cols_numericas = ["tempo", "custo", "venda", "minimo", "maximo"]
    df_template = limpar_dados_numericos(df_template, cols_numericas)

    df_template["lucro_unitario"] = df_template["venda"] - df_template["custo"]

    df_template["tempo"] = df_template["tempo"].replace(0, 0.01)
    df_template["rentabilidade_hora"] = (
        df_template["lucro_unitario"] / df_template["tempo"]
    )

    if df_realizado is not None:
        df_realizado.columns = df_realizado.columns.str.lower().str.strip()
        if "quantidade" in df_realizado.columns:
            df_realizado = limpar_dados_numericos(df_realizado, ["quantidade"])
            df_real_ok = df_realizado[["servico", "quantidade"]].copy()
        else:
            df_real_ok = pd.DataFrame(
                {"servico": df_template["servico"], "quantidade": 0}
            )
    else:
        df_real_ok = pd.DataFrame({"servico": df_template["servico"], "quantidade": 0})

    df_final = pd.merge(
        df_template, df_real_ok, on="servico", how="left", suffixes=("", "_real")
    )

    df_final["quantidade_real"] = df_final["quantidade"].fillna(0)
    if "quantidade" in df_final.columns:
        del df_final["quantidade"]

    return df_final
