from bs4 import BeautifulSoup
import requests
import re
import datetime as dt
from tqdm import tqdm
import pandas as pd
import argparse
import os
from konlpy.tag import Kkma, Okt

# Assuming utils functions are defined here if not in utils.py
def str_to_time(s, format='%Y.%m.%d %H:%M'):
    return dt.datetime.strptime(s, format)

def remove_stopword(text):
    # Implement your stopword removal logic
    return text

def remove_symbol(text):
    # Implement your symbol removal logic
    return text

def remove_blank(text):
    # Implement your blank removal logic
    return text

def pos_tag(text, tokenizer):
    return tokenizer.pos(text)

def remove_num_alpha_only(text, pos_tagged):
    # Implement your logic to remove number/alpha only
    return text

def remove_long_number(text, pos_tagged):
    # Implement your logic to remove long numbers
    return text

def crawler(codes, max_page, startdate, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", "referer": "https://finance.naver.com/item/board.naver?code=028300"}):
    result_df = pd.DataFrame([])
    start_date = dt.datetime.strptime(startdate, "%Y-%m-%d")
    
    for page in tqdm(range(20200, 21200)):
        url = f"https://finance.naver.com/item/board.naver?code={codes}&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
            continue
        
        html_content = response.content
        soup = BeautifulSoup(html_content.decode('euc-kr', 'replace'), 'html.parser')
        
        table = soup.find('table', {'class': 'type2'})
        
        if table is None:
            print(f"Failed to find the table on page {page}")
            continue
        
        tb = table.select('tbody > tr')

        for row in tb:
            try:
                if len(row.select('td > span')) > 0:
                    date = row.select('td > span')[0].text
                    date = str_to_time(date, '%Y.%m.%d %H:%M')

                    if start_date > date:
                        print(f'comment from {date} done!')
                        return result_df

                    title = row.select('td.title > a')[0]['title']
                    user = row.select('td.p11')[0].text
                    views = row.select('td > span')[1].text
                    recommends = row.select('td > strong')[0].text
                    unrecommends = row.select('td > strong')[1].text

                    table = pd.DataFrame({'date': [date], 'title': [title], 'user': [user], 'views': [views], 'recommends': [recommends], 'unrecommends': [unrecommends]})
                    result_df = pd.concat([result_df, table], ignore_index=True)
            except (IndexError, AttributeError) as e:
                print(f"Skipping row due to error: {e}")
                continue

    return result_df

def preprocess(df, company, output_dir):
    tokenizer = Okt()

    df['title'] = df['title'].apply(remove_stopword)
    df['title'] = df['title'].apply(remove_symbol)
    df['title'] = df['title'].apply(remove_blank)

    df['pos_tagged'] = df['title'].apply(lambda i: pos_tag(i, tokenizer=tokenizer))

    df['title'] = df.apply(lambda i: remove_num_alpha_only(i['title'], i['pos_tagged']), axis=1)
    df['title'] = df.apply(lambda i: remove_long_number(i['title'], i['pos_tagged']), axis=1)

    df = df[(df['title'] != '') & (df['pos_tagged'] != None)]

    result = df[['date', 'title', 'user', 'views', 'recommends', 'unrecommends']]

    # Create directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    result.to_csv(f'20200_21200.csv', encoding='utf-8-sig', index=False)
    print(f'{output_dir}/comment_{company}.csv saved!')

    return None

parser = argparse.ArgumentParser()
parser.add_argument('--max_page', type=int, default=10000)
parser.add_argument('--ticker', type=str, default='028300')
parser.add_argument('--company', type=str, default='HLB')
parser.add_argument('--output_dir', type=str, default='./output')
parser.add_argument('--startdate', type=str, default='2020-07-21')

if __name__ == "__main__":
    args = parser.parse_args()
    df = crawler(args.ticker, args.max_page, args.startdate)
    preprocess(df, company=args.company, output_dir=args.output_dir)
