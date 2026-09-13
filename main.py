import requests
import pandas as pd
import json
from pydantic import BaseModel, Field
from fastapi import FastAPI
from banco_central_api import gerador_juros_reais


class SimulacaoRequest(BaseModel):
    data_inicio: str = Field(...,description="Data de início do investimento. Use o formato DD/MM/AAAA.",examples=["01/01/2020"]) #... = obrigatorio
    data_fim: str = Field(...,description="Data de fim do investimento, ou seja, retirada do mesmo. Use o formato DD/MM/AAAA",examples=["01/01/2021","02/12/1999"])
    valor_investido: float = Field(...,description="Valor total investido em Reais (R$).", examples=[1000.00])
    percentual_cdi: float = Field(...,description="Valor total investido em Reais (R$).",examples=[1000.00])


app = FastAPI(title="Bond Investment Simulator", version="1.0.0")

@app.post("/simular-cdi")
def simulador(req: SimulacaoRequest):
    result = gerador_juros_reais(req.data_inicio,req.data_fim,req.valor_investido,req.percentual_cdi)
    return result
    