# 00_extrair_pib_ibge.py
# Dados manuais extraídos dos documentos (valores em R$)
# Fonte: https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9088-produto-interno-bruto-dos-municipios.html?=&t=resultados

import os
import pandas as pd

# 1) Defina os caminhos dos arquivos
arquivo_antigo = "data/raw/PIB dos Municípios - base de dados 2002-2009.xls"
arquivo_novo = "data/raw/PIB dos Municípios - base de dados 2010-2021.xlsx"

# 2) Lista de códigos IBGE dos municípios de Serra do Penitente
municipios_alvo = ["2100501", "2101400", "2112001"]

# Criar diretórios, se necessário
os.makedirs("data/partial", exist_ok=True)


def carregar_e_filtrar(path: str, engine: str) -> pd.DataFrame:
    # lê toda a planilha “PIB dos Municípios”
    df = pd.read_excel(
        path,
        sheet_name="PIB_dos_Municípios",
        engine=engine,
        dtype={"Código do Município": str},
    )
    # filtra somente pelos códigos e renomeia colunas-chaves
    df = df[df["Código do Município"].isin(municipios_alvo)].copy()
    df.rename(columns={
        "Código do Município": "codigo_ibge",
        "Nome do Município":   "municipio",
        "Ano":                 "ano",
    }, inplace=True)
    return df


# 3) Carrega cada base
df_2002_2009 = carregar_e_filtrar(arquivo_antigo, engine="xlrd")
df_2010_2021 = carregar_e_filtrar(arquivo_novo,   engine="openpyxl")

# 4) Concatena as duas faixas de ano
df_concat = pd.concat([df_2002_2009, df_2010_2021], ignore_index=True)

# 5) (Opcional) ordena por município e ano
df_concat.sort_values(["codigo_ibge", "ano"], inplace=True)

# 6) Exporta para CSV
output_path = "data/partial/pib_municipal_serra_penitente_ibge.csv"
df_concat.to_csv(output_path, index=False)

print(f"✅ CSV gerado em: {output_path}")
