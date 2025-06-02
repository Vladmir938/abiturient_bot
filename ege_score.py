import requests
import pandas as pd
from io import StringIO

url = 'https://entrant.zabgu.ru/?page_id=130'
response = requests.get(url)
response.raise_for_status()

tables = pd.read_html(StringIO(response.text))
df_raw = tables[0]

df_raw.dropna(how='all', inplace=True)
df_raw.columns = df_raw.iloc[0]
df = df_raw[1:].reset_index(drop=True)

df.replace("—", pd.NA, inplace=True)

# Переименование колонок
df.rename(columns={
    "№ п/п": "id",
    "Вступительное испытание": "name",
    "Количество баллов, min": "min_score",
    "Количество баллов ЕГЭ, max": "max_score",
    "Кол-во баллов по вузовским вступительным испытаниям, max": "accept_score"
}, inplace=True)

# Приведение типов: id - int, баллы - int или None
df['id'] = df['id'].astype(int)
for col in ['accept_score', 'min_score', 'max_score']:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

df.to_json("entrance_exam_scores.json", orient="records", force_ascii=False, indent=2)
