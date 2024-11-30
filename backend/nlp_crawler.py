from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import spacy

app = Flask(__name__)
CORS(app)

# API endpoint
@app.route('/api/crawl_data', methods=['POST'])

def crawl_data():
    
    user_input = request.json.get('input')
    # Receive "user_input" variable
    product_input = str(request.get_json())
    i = 0
    product = ''
    for words in product_input.split(' '):
        if i == (len(product_input.split(' '))-1):
            product = product + words
        else: 
            product = product + words + '-'
        i += 1
    
    # Count number of subpages
    url = f'https://www.kleinanzeigen.de/s-{product}/k0'
    p = requests.get(url)
    website_data = BeautifulSoup(p.text, 'html.parser')
    number_of_pages = len(website_data.find_all('a', {'class': 'pagination-page'}))

    # Get productlist
    def get_productlist(url):
        # check each page
        for i in range(1,number_of_pages): 
            if i > 1: 
                url = f'https://www.kleinanzeigen.de/s-seite:{i}/{product}/k0'
            # get html content
            r = requests.get(url)
            html_content = BeautifulSoup(r.text, 'html.parser')
            # get productlist
            if i == 1:
                productslist = []
            results = html_content.find_all('div', {'class': 'aditem-main'})
            for item in results:
                if item.find('a', {'class': 'ellipsis'}) is not None:
                    products = {
                        'title': item.find('a', {'class': 'ellipsis'}).text.replace(',','.'),
                        'price': int(item.find('p', {'class': 'aditem-main--middle--price-shipping--price'}).text.replace(' ','').replace('\n','').replace('.','').split("€")[0].replace('VB','0').replace('Zuverschenken','0').replace('"','0')),
                        'link': item.find('a', {'class': 'ellipsis'})['href']
                    }
                productslist.append(products)
        return productslist

    # Create and copy data.frame
    def create_dataframe(productslist):
        df_products = pd.DataFrame(productslist)
        df_products = df_products.sort_values(by=['price'])
        df_products = df_products.drop_duplicates()
        return df_products
    df_products = create_dataframe(get_productlist(url))
    df_products_detailed = df_products.copy()
    df_products_detailed["description"] = ' '

    # Get product description of each product
    for i, row in df_products.iterrows():
        if isinstance(row['link'], str):
            url = 'https://www.kleinanzeigen.de' + row['link']
            description = ''
            q = requests.get(url)
            if q.status_code == 200:
                html_content = BeautifulSoup(q.text, 'html.parser')
                for br_tag in html_content.find_all('br'): # handle line breaks
                    br_tag.insert_before(' ')
                    br_tag.unwrap()
                if html_content.find('p', {'id': 'viewad-description-text'}) is not None:
                    description = html_content.find('p', {'id': 'viewad-description-text'}).text.replace('\n', ' ').replace('-', ' ').replace('  ', '')
            else:
                description = 'Error loading page'
            # add description in data.frame
            df_products_detailed.at[i, 'description'] = description
            # reduce server load
            time.sleep(1)
    # add title information in product description
    df_products_detailed['description'] = df_products_detailed['title'] + ' ' + df_products_detailed['description']  
        
    # Extract shutter count
    def extract_shutter_count(description):
        match = re.search(r'(\d{1,3}(\.\d{3})*)(\smal)?(\s+(A|a)+(us)((ge)?)+(lös))|(A|a)(uslösung)\w+?\s(\d{4})', description, re.IGNORECASE)
        if match:
            if match.group(1) == None:
                try:
                    value = int(match.group(11))
                except ValueError:
                    return None
                else:
                    return int(match.group(11)) # returns last group () = number
            else:
                return int(match.group(1).replace('.', '')) # returns first group () = number
        else:
            return None
    df_products_detailed['shutter_count'] = df_products_detailed['description'].apply(extract_shutter_count)
    df_products_detailed['shutter_count'] = pd.to_numeric(df_products_detailed['shutter_count'], errors='coerce')
    df_products_detailed['shutter_count'] = df_products_detailed['shutter_count'].fillna(0).astype(int)
    df_products_detailed['shutter_count'] = df_products_detailed['shutter_count'].astype(int)

    # Check for good camera condition
    pattern = r'(\d{1,5}(?:[\.,]?\d{1,3})?)\s?(Auslösungen?|Bilder?|Fotos?)(\s?(wenig|kaum|nie|selten|nicht|fast|geringe)\s?(genutzt|verwendet|gemacht|fotografiert)?)?'
    def check_condition(description):
        if len(re.findall(pattern, description)) != 0:
            return(True)
        else: 
            return(False)
    df_products_detailed['new?'] = df_products_detailed['description'].apply(check_condition)

    # NLP preprocessing 1 - Stop words & tokenization
    nlp = spacy.load('de_core_news_sm') # Load German model
    from spacy.lang.de.stop_words import STOP_WORDS
    def preprocess(text): # remove stop words function
        doc = nlp(text)
        no_stop_words = [token.text for token in doc if not token.is_stop and not token.is_punct]
        return ' '.join(no_stop_words)
    df_products_detailed['description_pp'] = df_products_detailed['description'].apply(preprocess)

    # NLP preprocessing 2 - Lemmatization
    doc = nlp(df_products_detailed['description_pp'][2])
    def preprocess2(text):
        doc = nlp(text)
        lemmata = [token.lemma_ for token in doc if not token.is_space]
        return lemmata
    df_products_detailed['description_pp'] = df_products_detailed['description_pp'].apply(preprocess2).apply(lambda x: ' '.join(x))

    # NLP preprocessing 3 - delete punctuation and spaces
    def preprocess3(text):
        text = re.sub(r'(\d)[,.](\d)', r'\1<DOT>\2', text)
        text = re.sub(r'(\d)[,.](\d+)(?=\D)', r'\1<DOT>\2', text) 
        text = re.sub(r'[.,!?\-]+', ' ', text)
        text = text.replace('<DOT>', '.') # replace deleted dots and commas back to dots
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        text = text.lower() # lower case reduces dimension in simpler ML models
        return text
    df_products_detailed['description_pp'] = df_products_detailed['description_pp'].apply(preprocess3)

    # return as json
    return jsonify(df_products_detailed.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
