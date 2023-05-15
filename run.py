import requests
from bs4 import BeautifulSoup
import re
import json

url_participants = ['albania','armenia','australia','austria','azerbaijan','belgium','croatia','cyprus','czechia','denmark','estonia','finland','france','georgia','germany','greece','iceland','ireland','israel',
    'italy','latvia','lithuania','malta','moldova','netherlands','norway','poland','portugal','romania','san-marino','serbia','slovenia','spain','sweden','switzerland','ukraine','united-kingdom']

# header for request
headerString = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
Chrome / 41.0 .2272 .101 Safari / 537.36 '

scoring = {}

for url_country in url_participants:
    url = 'https://eurovision.tv/event/liverpool-2023/grand-final/results/'+url_country

    # new session for request
    session = requests.Session()

    headers = {'User-Agent': headerString}

    # perform get request
    contents = session.get(url, headers=headers)

    # read encoding of contents
    encoding = contents.encoding if 'charset' in contents.headers.get(
        'content-type', '').lower() else None

    # create BeatifulSoup Html reader instance with correct encoding
    soup = BeautifulSoup(
        contents.content, from_encoding=encoding, features="html.parser")


    table = soup.findAll('tr')

    countries = [i.text for i in table]

    country_dict = {}
    for entry in countries[1:]:
        country_name = None
        country_voting = None
        country_points = 0
        for line in entry.split('\n'):
            if re.match(r'^\D+$', line):
                country_name = line
            elif re.match(r'.*\d+\w{2}$', line):
                split_line = line.split(' ')
                country_voting = split_line[-1][:-2]
                if len(split_line) > 1:
                    country_points = split_line[0]
        if country_name in scoring:
            scoring[country_name].append((url_country,int(country_voting),int(country_points)))
        else:
            scoring[country_name] = [(url_country,int(country_voting),int(country_points))]

ranking = []

with open('raw.txt', 'w') as f:
    for key, values in scoring.items():
        televoter_points = sum([i[2] for i in values])
        avg_place = round(sum(i[1] for i in values)/36,2)
        ranking.append((key,televoter_points,avg_place))
    print(json.dumps(scoring), file=f)

with open('by_points.txt', 'w') as f:
    j = 0
    for value in sorted(ranking, key=lambda x: x[1], reverse=True):
        j+=1
        print(str(j)+'.\t'+str(value[1])+'\t'+value[0], file=f)

with open('by_avg.txt', 'w') as f:
    j = 0
    for value in sorted(ranking, key=lambda x: x[2]):
        j+=1
        print(str(j)+'.\t'+str(value[2])+'\t'+value[0], file=f)