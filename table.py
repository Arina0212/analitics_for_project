import csv
import re
import datetime
from typing import List
from matplotlib.axes import Axes
import matplotlib.pyplot as plt

currency_to_rub = {"AZN": 35.68,
                   "BYR": 23.91,
                   "EUR": 59.90,
                   "GEL": 21.74,
                   "KGS": 0.76,
                   "KZT": 0.13,
                   "RUR": 1,
                   "UAH": 1.64,
                   "USD": 60.66,
                   "UZS": 0.0055}

class DataSet:
    def __init__(self, file_name):
        self.file_name = file_name
        self.vacancies = [Vacancy(vac) for vac in self.csv_filer(*self.csv_reader(file_name))]

    def delete_html(self, n_html):
        result = re.compile(r'<[^>]+>').sub('', n_html)
        return result if '\n' in n_html else " ".join(result.split())

    def csv_reader(self, file_name):
        file_csv = open(file_name, encoding='utf_8_sig')
        vacanc_reader_name = file_csv.readline().rstrip().split(",")
        reader_csv = csv.reader(file_csv)
        vacanc_reader = [x for x in reader_csv]
        vacanc_reader_corr = [x for x in vacanc_reader if len(x) == len(vacanc_reader_name) and ' ' not in x]
        return vacanc_reader_name, vacanc_reader_corr

    def csv_filer(self, name, vacancies):
        vacancies_list = list(filter(lambda vac: (len(vac) == len(name) and vac.count('') == 0), vacancies))
        vacanies_dict = [dict(zip(name, map(self.delete_html, vac))) for vac in vacancies_list]
        return vacanies_dict

class Vacancy:
    def __init__(self, dictionary):
        self.name = dictionary['name']
        self.salary = Salary(dictionary['salary_from'], dictionary['salary_to'], dictionary['salary_currency'])
        self.area_name = dictionary['area_name']
        self.published_at = dictionary['published_at']

class Salary:
    def __init__(self, salary_from, salary_to, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_currency = salary_currency

    def to_rub(self, new_salary: float) -> float:
        return new_salary * currency_to_rub[self.salary_currency]


class Report:
    def __init__(self, years_salary, years_vacs_count, prof_years_salary, prof_years_vacs_count, city_salary,
                 city_vacs_rate):
        self.years_salary = years_salary
        self.years_vacs_count = years_vacs_count
        self.prof_years_salary = prof_years_salary
        self.prof_years_vacs_count = prof_years_vacs_count
        self.city_salary = city_salary
        self.city_vacs_rate = city_vacs_rate

    def create_regular_schedule(self, ax: Axes, keys1, keys2, values1, values2, label1, label2, title):
        x1 = [key - 0.2 for key in keys1]
        x2 = [key + 0.2 for key in keys2]
        ax.bar(x1, values1, width=0.4, label=label1)
        ax.bar(x2, values2, width=0.4, label=label2)
        ax.legend()
        ax.set_title(title, fontsize=16)
        ax.grid(axis="y")
        ax.tick_params(axis="x", labelrotation=90)

    def create_pie_schedule(self, ax: Axes, title):
        new_dict = self.city_vacs_rate
        new_dict["Другие"] = 1 - sum([value for value in new_dict.values()])
        ax.pie(x=list(new_dict.values()), labels=list(new_dict.keys()))
        ax.axis('equal')
        ax.tick_params(axis="both", labelsize=6)
        plt.rcParams['font.size'] = 16
        ax.set_title(title, fontsize=16)

    def create_horizontal_schedule(self, ax: Axes, keys, values, title):
        keys = [key.replace(" ", "\n").replace("-", "-\n") for key in list(keys)]
        ax.barh(keys, values)
        ax.set_yticks(keys)
        ax.set_yticklabels(labels=keys, verticalalignment="center", horizontalalignment="right")
        ax.invert_yaxis()
        ax.set_title(title, fontsize=16)
        ax.grid(axis="x")
        ax.tick_params(axis='y', labelsize=6)

    def generate_schedule(self):
        fig, axis = plt.subplots(2, 2)
        plt.rcParams['font.size'] = 8
        self.create_regular_schedule(axis[0, 0], self.years_salary.keys(), self.prof_years_salary.keys(),
                                     self.years_salary.values(), self.prof_years_salary.values(),
                                     "Средняя з/п", "з/п " + vacancy , "Уровень зарплат по годам")

        self.create_regular_schedule(axis[0, 1], self.years_vacs_count.keys(), self.prof_years_vacs_count.keys(),
                            self.years_vacs_count.values(), self.prof_years_vacs_count.values(),
                            "Количество вакансий", "Количество вакансий " + vacancy, "Количество вакансий по годам")

        self.create_horizontal_schedule(axis[1, 0], self.city_salary.keys(), self.city_salary.values(),
                                        "Уровень зарплат по городам")

        self.create_pie_schedule(axis[1, 1], "Доля вакансий по городам")

        fig.set_size_inches(16, 9)
        fig.tight_layout(h_pad=2)
        fig.savefig("graph.png")


def get_data(date):
    new_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
    return int(new_date.strftime('%Y'))

def get_statistic(result, index, n_message, slice=0, reverse=False):
    slice = len(result) if slice == 0 else slice
    statistic = dict(sorted(result, key=lambda item: item[index], reverse=reverse)[:slice])
    print(f'{n_message}{str(statistic)}')
    return statistic

def get_vacancies_statistic(vacs_list: List[Vacancy], fields, vac_name: str = ''):
    statistic_result = {}
    for vac in vacs_list:
        if vac.__getattribute__(fields) not in statistic_result.keys():
            statistic_result[vac.__getattribute__(fields)] = 0

    if vac_name != '':
        vacs_list = list(filter(lambda item: vac_name in item.name, vacs_list))
    for vac in vacs_list:
        statistic_result[vac.__getattribute__(fields)] += 1

    if fields == 'area_name':
        for key in statistic_result.keys():
            statistic_result[key] = round(statistic_result[key] / len(data.vacancies), 4)

    return statistic_result

def get_salary_statistic(vacs_list: List[Vacancy], fields, vac_name: str = ''):
    statistic_result = {}
    for vac in vacs_list:
        if vac.__getattribute__(fields) not in statistic_result.keys():
            statistic_result[vac.__getattribute__(fields)] = []
    if vac_name != '':
        vacs_list = list(filter(lambda item: vac_name in item.name, vacs_list))

    for vac in vacs_list:
        salary_to = vac.salary.salary_to
        salary_from = vac.salary.salary_from
        statistic_result[vac.__getattribute__(fields)].append(
            vac.salary.to_rub(float(salary_from) + float(salary_to)) / 2)

    for key in statistic_result.keys():
        statistic_result[key] = int(sum(statistic_result[key]) // len(statistic_result[key])) if len(
            statistic_result[key]) != 0 else 0

    return statistic_result


file = input("Введите название файла: ")
vacancy = input("Введите название профессии: ")
data = DataSet(file)
new_dict = {}

for vacs in data.vacancies:
    vacs.published_at = get_data(vacs.published_at)
    if vacs.area_name not in new_dict.keys():
        new_dict[vacs.area_name] = 0
    new_dict[vacs.area_name] += 1

needed_vacs = list(filter(lambda x: int(len(data.vacancies) * 0.01) <= new_dict[x.area_name], data.vacancies))
years_salary = get_statistic(get_salary_statistic(data.vacancies, 'published_at').items(), 0,
                             'Динамика уровня зарплат по годам: ')
years_vacs_count = get_statistic(get_vacancies_statistic(data.vacancies, 'published_at').items(), 0,
                                 'Динамика количества вакансий по годам: ')
prof_years_salary = get_statistic(get_salary_statistic(data.vacancies, 'published_at', vacancy).items(), 0,
                                  'Динамика уровня зарплат по годам для выбранной профессии: ')
prof_years_vacs_count = get_statistic(get_vacancies_statistic(data.vacancies, 'published_at', vacancy).items(), 0,
                                      'Динамика количества вакансий по годам для выбранной профессии: ')
city_salary = get_statistic(get_salary_statistic(needed_vacs, 'area_name').items(), 1,
                            'Уровень зарплат по городам (в порядке убывания): ', 10, True)
city_vacs_rate = get_statistic(get_vacancies_statistic(needed_vacs, 'area_name').items(), 1,
                               'Доля вакансий по городам (в порядке убывания): ', 10, True)

report = Report(years_salary, years_vacs_count, prof_years_salary, prof_years_vacs_count, city_salary,
       city_vacs_rate)
report.generate_schedule()