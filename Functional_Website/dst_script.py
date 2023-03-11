import csv
import os
from flask import Flask, render_template
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
import pandas as pd

def dst_process(filename):
    name = filename.split('\\')
    name = name[len(name)-1].split('.')
    name = name[0]
    data = {'Name': ['MR.BEANS','MR.BEANS','MR.BEANS'], 'Status': ['LOL','LOL','LOL']}
    # df_hotel_output = pd.read_csv(filename)
    df_hotel_output = pd.DataFrame(data)

    # Processing 
    

    output_file = f'result_{name}.csv'
    with open(os.path.join('output', output_file), 'w', newline='',encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Status'])

        for i in range(len(df_hotel_output)):
            writer.writerow([df_hotel_output["Name"][i], df_hotel_output["Status"][i]])

    return output_file,df_hotel_output