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
    fator_cdi_usuario = percentual_cdi / 100  # 110 / 100 = 1.1
    cdi_mensal_decimal = df_final['valor_cdi'] / 100
    
    # A rentabilidade final do mês é o CDI * O percentual do usuário
    df_final['rentabilidade_do_mes'] = cdi_mensal_decimal * fator_cdi_usuario
    df_final['fator_investimento'] = 1 + df_final['rentabilidade_do_mes']
    

    df_final['inflacao_acumulada'] = df_final['fator_inflacao'].cumprod() #multiplicacao acumulando valor
    df_final['investimento_acumulado'] = df_final['fator_investimento'].cumprod()

    tempo_meses = len(df_final)
    resultado_final = df_final.iloc[-1] #ultimo item
    
    valor_bruto_final = valor_investido * resultado_final['investimento_acumulado']
    lucro_final = valor_bruto_final - valor_investido
    
    #calculo imposto de renda
    if tempo_meses <= 6:
        aliquota_ir = 0.225
    elif tempo_meses <= 12:
        aliquota_ir = 0.20
    elif tempo_meses <= 24:
        aliquota_ir = 0.175
    else:
        aliquota_ir = 0.15
        
    imposto_retido = lucro_final * aliquota_ir
    valor_liquido_final = valor_bruto_final - imposto_retido
    
    # 6. Ganho Real (Descontando a inflação do valor líquido)
    inflacao_periodo = resultado_final['inflacao_acumulada']
    ganho_real_liquido = ((valor_liquido_final / valor_investido) / inflacao_periodo) - 1
    
    return {
        "parametros": {
            "periodo_meses": tempo_meses,
            "valor_investido": valor_investido,
            "percentual_cdi": f"{percentual_cdi}%"
        },
        "rentabilidade_bruta": {
            "valor_bruto_final": float(round(valor_bruto_final, 2)),
            "lucro_bruto": float(round(lucro_final, 2))
        },
        "imposto_de_renda": {
            "aliquota_aplicada": f"{aliquota_ir * 100}%",
            "imposto_descontado": float(round(imposto_retido, 2)),
            "valor_liquido_final": float(round(valor_liquido_final, 2))
        },
        "analise_real": {
            "inflacao_acumulada_pct": float(round((inflacao_periodo - 1) * 100, 2)),
            "ganho_real_liquido_pct": float(round(ganho_real_liquido * 100, 2))
        }
    }
    

if __name__ == '__main__':
    print(gerador_juros_reais('12/05/2020','12/05/2027',120.5,110))