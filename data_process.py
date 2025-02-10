import pandas as pd
from unidecode import unidecode
import re

df = pd.read_csv('resultados_parciais.csv')

# Processamento dos dados

area_map = {
    'area[SQ001]': 'Ciências Exatas e da Terra',
    'area[SQ002]': 'Ciências Biológicas',
    'area[SQ003]': 'Engenharias',
    'area[SQ004]': 'Ciências da Saúde',
    'area[SQ005]': 'Ciências Agrárias',
    'area[SQ006]': 'Ciências Sociais Aplicadas',
    'area[SQ007]': 'Ciências Humanas',
    'area[SQ008]': 'Linguística, Letras e Artes',
    'area[SQ009]': 'Outros'
}

# Criando a Series gde_area
gde_area = pd.Series(index=df.index, dtype=object)

for col, area in area_map.items():
    gde_area[df[col] == "Sim"] = area

# Adicionando a Series ao DataFrame original (opcional)
df['gde_area'] = gde_area
df['gde_area'] = df['gde_area'].astype(str)

# Função para remover acentos e transformar texto em minúsculas
def process_text(text):
    if pd.isnull(text):
        return ""
    return unidecode(text).lower()

# Aplicar a função a cada coluna em colunas_tipo
colunas_tipo = [
    'iniciativa[SQ001_SQ003]', 
    'iniciativa[SQ002_SQ003]', 
    'iniciativa[SQ003_SQ003]', 
    'iniciativa[SQ004_SQ003]', 
    'iniciativa[SQ005_SQ003]'
]

for col in colunas_tipo:
    df[col] = df[col].apply(process_text)

# Inicializar as novas colunas
df['extensão'] = 0
df['ensino'] = 0
df['pesquisa'] = 0

# Contar as ocorrências das palavras e atualizar as novas colunas
for col in colunas_tipo:
    df['extensão'] += df[col].str.contains('extensao').astype(int)
    df['ensino'] += df[col].str.contains('ensino').astype(int)
    df['pesquisa'] += df[col].str.contains('pesquisa').astype(int)

area_extensao_map = {
    'areaextensao[SQ001]': 'Comunicação',
    'areaextensao[SQ002]': 'Cultura',
    'areaextensao[SQ003]': 'Direitos Humanos e Justiça',
    'areaextensao[SQ004]': 'Educação',
    'areaextensao[SQ005]': 'Meio Ambiente',
    'areaextensao[SQ006]': 'Saúde',
    'areaextensao[SQ007]': 'Tecnologia e Produção',
    'areaextensao[SQ008]': 'Trabalho'
}

# Criando a Series area_extensao
area_extensao = pd.Series(index=df.index, dtype=object)

for col, area in area_extensao_map.items():
    area_extensao[df[col] == "Sim"] = area

# Adicionando a Series ao DataFrame original (opcional)
df['area_extensao'] = area_extensao

df['gde_area'] = df['gde_area'].astype(str)

df['area_extensao'] = df['area_extensao'].astype(str)