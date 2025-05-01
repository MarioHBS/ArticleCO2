# path: src/create_pib_municipal_serra_penitente.py

import pandas as pd
import os

# Criar diretório para salvar o arquivo
os.makedirs("data/generated", exist_ok=True)

# Dados manuais extraídos dos documentos (valores em R$)
municipal_pib_data = [
    {"municipio": "Balsas", "codigo_ibge": 2101400, "ano": 2021, "pib": 6307609566},
    {"municipio": "Tasso Fragoso", "codigo_ibge": 2112001,
        "ano": 2021, "pib": 2351451559},
    {"municipio": "Alto Parnaíba", "codigo_ibge": 2100501,
        "ano": 2021, "pib": 578991387},
]

# Criar o DataFrame
df_municipal_pib = pd.DataFrame(municipal_pib_data)

# Salvar em CSV
output_path = "data/generated/pib_municipal_serra_penitente.csv"
df_municipal_pib.to_csv(output_path, index=False)

print(f"✅ Arquivo salvo com sucesso: {output_path}")
print(df_municipal_pib)
