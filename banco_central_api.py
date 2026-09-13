import requests
import pandas as pd
import json


def busca_serie_temporal(codigo_sgs,data_inicio,data_fim):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_sgs}/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}"

    requisicao = requests.get(url= url)
    if requisicao.status_code != 200:
        print("Erro ao consultar API")

    dados = requisicao.json()
    if not dados:
        print("Erro ao acessar os dados do retorno da API")
    else:
        df = pd.DataFrame(dados)
        df['valor'] = pd.to_numeric(df['valor'])
        return df
    return 

def gerador_juros_reais(data_inicio,data_fim,valor_investido,percentual_cdi):
    df_ipca = busca_serie_temporal(433,data_inicio,data_fim) #IPCA
    df_cdi = busca_serie_temporal(4391,data_inicio,data_fim) #CDI

    df_ipca = df_ipca.rename(columns={"valor":"valor_ipca"})
    df_cdi = df_cdi.rename(columns={"valor":"valor_cdi"})

    df_final = pd.merge(df_ipca,df_cdi,how="inner",on="data")
    
    df_final['fator_inflacao'] = 1 + (df_final['valor_ipca'] / 100)

    # Se o CDB rende 110% do CDI, multiplicamos o CDI do mês por 1.1 antes de criar o fator
    df_final['rentabilidade_do_mes'] = (df_final['cdi_mensal_pct'] / 100) * percentual_cdi
    df_final['fator_investimento'] = 1 + df_final['rentabilidade_do_mes']


    df_final['inflacao_acumulada'] = df_final['fator_inflacao'].cumprod()
    df_final['investimento_acumulado'] = df_final['fator_investimento'].cumprod()

    #calculo imposto de renda
    #len(df_final) e tabela regressiva
    

if __name__ == '__main__':
    df = busca_serie_temporal(4391,'12/05/2020','12/05/2022')
    print(df)