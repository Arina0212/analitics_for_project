import csv
import math
import re


def main():
    for i in range(2003, 2023):
        data = read_file('vacancies_with_skills.csv')

        dataf = clean_data(data, i)
        print(f'{i} = {list(take_skills(dataf))[:10]}')

def take_skills(main_data):
    data = []
    data_dict = {}
    for skills in map(lambda x: x['key_skills'], main_data):
        for skill in skills:
            if skill not in data_dict:
                data_dict[skill] = 1
            else:
                data_dict[skill] += 1
    for skill in data_dict:
        data.append([skill, data_dict[skill]])
    return dict(sorted(data_dict.items(), key=lambda x: x[1], reverse=True)).keys()

def read_file(name):
    flag = True
    counter = 0
    data = []
    with open(name, encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        heading = next(reader)
        data.append(heading)
        for row in reader:
            for piece in row:
                if len(piece) == 0:
                    flag = False
                counter += 1
            if flag and (len(heading) == counter):
                data.append(row)
            flag = True
            counter = 0
    return data


def clean_data(data, date):
    pattern = re.compile('<.*?>')
    pattern1 = re.compile('\s+')
    heading = data[0]
    chk_pat = '(?:{})'.format(
        '|'.join(['design', 'ux', 'ui', 'дизайн', 'иллюстратор']))
    alfa = data
    alfa.pop(0)
    data_new = []
    for row in alfa:
        dict_new = {}
        for i in range(0, len(heading)):
            if heading[i] == 'key_skills':
                dict_new[heading[i]] = row[i].split("\n")
            else:
                row[i] = row[i].replace("\n", ", ")
                row[i] = re.sub(pattern, '', row[i])
                row[i] = re.sub(pattern1, ' ', row[i])
                row[i] = row[i].strip()
                dict_new[heading[i]] = row[i]
        if re.search(chk_pat, row[1].lower(), flags=re.I) and str(date) == row[5][:4]:
            data_new.append(dict_new)
    return data_new
