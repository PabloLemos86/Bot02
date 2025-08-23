# config.py - configuração do bot

# Token do Bot (já incluído)
TOKEN = "8023106816:AAEB5QURW63jmPMZOntDxf-JcJzvWpflAV8"

# URL pública do webhook (definir no Render como variável de ambiente)
import os
WEBHOOK_URL = os.getenv('WEBHOOK_URL', f'https://sua-url-plataforma.com/{TOKEN}')

# Quantidade padrão de licitações retornadas
DEFAULT_QTD = 5

# Regiões e estados
REGIOES = {
    "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"],
    "Nacional": []
}