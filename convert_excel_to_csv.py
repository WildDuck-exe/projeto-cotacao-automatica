import pandas as pd

excel_file = "/home/ubuntu/upload/base_materiais_eletricos_1000_itens.xlsx"
csv_file = "/home/ubuntu/project/data/produtos.csv"

try:
    df = pd.read_excel(excel_file)
    df.to_csv(csv_file, index=False, encoding="utf-8")
    print(f"Arquivo {excel_file} convertido para {csv_file} com sucesso.")
except Exception as e:
    print(f"Erro ao converter o arquivo Excel para CSV: {e}")

