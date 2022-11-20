from datetime import datetime
from time import time
from loguru import logger
from pprint import pprint

import os
import re
import json
import csv

''' config'''
start_time = time()
path = os.path.dirname(os.path.realpath(__file__))
logger.add(f'log/log.log', 
           format= '{time} {level} {message}', 
           level='DEBUG', 
           serialize=False, 
           rotation='1 month', 
           compression='zip')
logger.info(f'Start app {datetime.today()}')

list_of_files =  os.listdir(f'{path}/in')

fields = (('Purchase Order Number', '\n'),
          ('Order Type', '\n'),
          ('Department','\n'),
          ('Ship To','GLN'),
          ('Supplier Name','\n'),
          ('Supplier Number','\n'),
          ('Total Units Ordered','\n'),
          ('Extended Cost','Assortment Items'),
          )
line_Item_fields = (('Item', 'GTIN'),
                    ('GTIN', 'Supplier Stock #'),
                    ('Supplier Stock #', 'Color'),
                    ('Quantity Ordered', 'UOM'),
                    ('Cost', 'Extended Cost'))


def find_segments(text, start, end):
    pattern = re.escape(start) + r'(.*?)' + re.escape(end)
    return ''.join(re.findall(pattern, text, flags=re.DOTALL)).strip()

def read_file(filename: str) -> dict:
    
    with open(filename, 'r') as f:
        data = {}
        line_Item = {}
        d = f.read()
        for field in fields:
            data.update({field[0]: find_segments(d, field[0], field[1])})
        for item in line_Item_fields:
            line = find_segments(d, item[0], item[1])
            if '\n\ns' in line:
                line = line.split('\n')[0]
            if 'Item' == item[0]:
                line_Item.update({'Item Number':line})
            else:
                line_Item.update({item[0]:line})
        f.close()
        data.update({'Line Item': line_Item})
    return data


def append_data() -> list:
    data = []
    for file in os.listdir(f'{path}/in'):
        filename = f'{path}/in/{file}'
        logger.info(f'read file {file}')
        
        data.append(read_file(filename))
    return data

data = append_data()


def create_json():

    json_object = json.dumps(data, indent=4)
    with open(f'{path}/out/data.json', "w") as outfile:
        outfile.write(json_object)




def create_csv():
    csv_fields = [field[0] for field in fields +  line_Item_fields]
    csv_fields = list(map(lambda field: field.replace('Item','Item Number'), csv_fields)) # replace Item to Item Number
    csv.register_dialect('myDialect', delimiter=';',
                         quoting=csv.QUOTE_ALL, quotechar='"')
                        
    with open(f'{path}/out/data.csv', 'w') as csvfile: 
        writer = csv.writer(csvfile, dialect='myDialect')
        writer.writerow(csv_fields) 
        for value in data:

            writer.writerow((value["Purchase Order Number"],
                            value["Order Type"],
                            value["Department"],
                            value["Ship To"],
                            value["Supplier Name"],
                            value["Supplier Number"],
                            value["Total Units Ordered"],
                            value["Extended Cost"],
                            value["Line Item"]["Item Number"],
                            value["Line Item"]["GTIN"],
                            value["Line Item"]["Supplier Stock #"],
                            value["Line Item"]["Quantity Ordered"],
                            value["Line Item"]["Cost"]))


@logger.catch
def main():
    create_json()
    create_csv()

if __name__ == '__main__':
    main()
    logger.info("--- %s seconds ---" % (time() - start_time))
    logger.info(f'End app {datetime.today()}')