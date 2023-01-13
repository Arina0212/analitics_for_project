import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def get_vacancy(page, day, is_until_noon):
    params = {
        'text': 'NAME:UX/UI дизайнер OR designer OR иллюстратор',
        "specialization": 1,
        'only_with_salary': True,
        "found": 1,
        "per_page": 100,
        "page": page,
        "date_from": f"2022-12-{day}T00:00:00+0300",
        "date_to": f"2022-12-{day}T11:59:00+0300",
    }
    if is_until_noon:
        params["date_from"] = f"2022-12-{day}T00:00:00+0300"
        params["date_to"] = f"2022-12-{day}T11:59:00+0300"
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return requests.get('https://api.hh.ru/vacancies', params).json()


day = input("Введите день:")

dataframe = pd.DataFrame(columns=["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"])
result = []
for i in range(2):
    for page in range(0, 999):
        response = get_vacancy(page, day, i)
        if (response['pages'] - page) == 0:
            break
        result.append(response)
for page in result:
    for vac in page["items"]:
        dataframe.loc[len(dataframe)] = [vac["name"], None, None, None, vac["area"]["name"], vac["published_at"]] \
            if vac["salary"] is None \
            else [vac["name"], vac["salary"]["from"], vac["salary"]["to"], vac["salary"]["currency"],
                  vac["area"]["name"], vac["published_at"]]
dataframe.to_csv(f'vacancies{day}.csv', index=False)
