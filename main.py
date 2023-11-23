import asyncio
import platform
import sys
import json
from datetime import datetime, timedelta
import httpx
from  httpx import AsyncClient
import os

url_bank = None
data_folder = os.getcwd()
class CastomError(Exception):
    pass


def parser_json_data(data: list)->list:
    result = []
    for element in data:
        intermediate_result = {
        element['date']: {
          'EUR': {
            'sale': None,
            'purchase': None
          },
          'USD': {
            'sale': None,
            'purchase': None
          }
        }
      }
        for elem in element["exchangeRate"]:
            currency = elem["currency"]
            if currency in ('USD', 'EUR'):
                intermediate_result[element['date']][currency] = {
                'sale' : elem["saleRateNB"],
                'purchase' : elem["purchaseRateNB"]}
        if None not in intermediate_result[element['date']]['EUR'].values() and None not in \
                intermediate_result[element['date']]['USD'].values():
            result.append(intermediate_result)
    with open(os.path.join(data_folder, 'data.json'), 'w') as file:
        json.dump(result, file, indent=4)
    return result


async def get_exchange_rates(url: str):
    async with httpx.AsyncClient() as client:
        cl = await client.get(url, timeout=20)
        if cl.status_code == 200:
            result = cl.json()
            return  result
        else:
            raise CastomError(f'Error: {cl.status_code} url: {url}')


async def main(day):
    if int(day) < 11:
        this_day = datetime.now().date()
        date_list = [(this_day - timedelta(days=x)).strftime("%d.%m.%Y") for x in range(int(day))]
        try:
            responses = await asyncio.gather(
                *[get_exchange_rates(f'https://api.privatbank.ua/p24api/exchange_rates?date={date}') for date in
                  date_list])
            return parser_json_data(responses)
        except:
            raise CastomError(f'Что-то пошло не так ')
    else:
        raise CastomError(f'{day} - недопустимый диапазон дней')

if __name__ == '__main__':
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(main(sys.argv[1]))
    print(result)

