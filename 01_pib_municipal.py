# path: src/01_pib_municipal.py

import os
import re
import unicodedata
import pandas as pd
import easyocr

# Dados manuais extraídos dos documentos (valores em R$)
# Fonte: https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9088-produto-interno-bruto-dos-municipios.html

# 1) Cria a pasta de saída
os.makedirs("data/partial", exist_ok=True)


def strip_accents_and_punct(s: str) -> str:
    """
    Remove acentos, pontuação extra e deixa em lowercase.
    """
    # NFD + remove acentos
    s = ''.join(c for c in unicodedata.normalize("NFD", s)
                if unicodedata.category(c) != "Mn")
    # remove tudo que não for letra, número ou espaço
    s = re.sub(r'[^A-Za-z0-9 ]+', ' ', s)
    return s.lower().strip()


def parse_municipio(text: str) -> dict:
    """
    Recebe o texto OCR e retorna:
      - municipio
      - codigo_ibge
      - pib_precos_correntes
      - impostos_liquidos
      - pib_per_capita
      - vab_total
      - vab_agro
      - vab_industria
      - vab_servicos
      - vab_adm_publica
    """
    linhas = [l.strip() for l in text.splitlines() if l.strip()]
    dados = {}

    # —————————————
    # 1) município e código IBGE na 1ª linha
    m = re.match(r"(.+?)\s+c[oó]digo[: ]+(\d+)", linhas[0], re.IGNORECASE)
    if m:
        dados["municipio"] = m.group(1).strip()
        dados["codigo_ibge"] = m.group(2).strip()

    # —————————————
    # 2) mapeia substrings para as colunas
    mapa = {
        "pib a precos correntes":  "pib_precos_correntes",
        "impostos":                 "impostos_liquidos",
        "pib per capita":          "pib_per_capita",
        "valor adicionado bruto":  "vab_total",
        "agropecuaria":            "vab_agro",
        "industria":               "vab_industria",
        "servicos":                "vab_servicos",
        "administracao":           "vab_adm_publica",
    }

    # percorre cada linha procurando a chave
    for i, linha in enumerate(linhas[1:], start=1):
        chave_raw = linha
        chave = strip_accents_and_punct(chave_raw)

        for key, col in mapa.items():
            if key in chave:
                # tenta pegar número na mesma linha
                txt = linha.replace(" ", "")
                mnum = re.search(r"([\d\.,]+)", txt)
                # ou na próxima
                if not mnum and i+1 < len(linhas):
                    mnum = re.search(
                        r"([\d\.,]+)", linhas[i+1].replace(" ", ""))
                if mnum:
                    num_txt = mnum.group(1).replace(".", "").replace(",", ".")
                    try:
                        valor = float(num_txt)
                    except ValueError:
                        valor = num_txt
                else:
                    valor = None

                dados[col] = valor
                print(f"  • Encontrou {col}: {valor}")
                break

    return dados


def processar_imagens():
    imagens = [
        ("data/raw/", "pib_alto_parnaiba.png"),
        ("data/raw/", "pib_balsas.png"),
        ("data/raw/", "pib_tasso_fragoso.png"),
    ]
    reader = easyocr.Reader(["pt"], gpu=False)
    registros = []

    for folder, filename in imagens:
        path = os.path.join(folder, filename)
        print(f"\n→ Processando {filename}…")
        texto = "\n".join(reader.readtext(path, detail=0, paragraph=True))
        print("→ Texto bruto OCR:\n", texto, "\n")
        rec = parse_municipio(texto)
        print("→ Registro extraído:", rec)
        registros.append(rec)

    # monta DataFrame e salva
    df = pd.DataFrame(registros)
    print("\nColunas detectadas:", df.columns.tolist())
    df = df[[
        "municipio", "codigo_ibge",
        "pib_precos_correntes", "impostos_liquidos", "pib_per_capita",
        "vab_total", "vab_agro", "vab_industria", "vab_servicos", "vab_adm_publica"
    ]]
    out = "data/partial/pib_municipal_serra_penitente.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n✅ CSV gerado em: {out}")


if __name__ == "__main__":
    processar_imagens()
