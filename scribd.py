#!/bin/python

from bs4 import BeautifulSoup
import requests
import argparse
import os
import shutil

BASE_URL = "https://www.scribd.com"

def extract_text(soup):
    extraction = ""
    for span in soup.find_all('span', {'class': 'a'}):
        extraction += span.get_text().encode('utf-8') + '\n'
    return extraction

def download_images(soup, title):
    train = 1
    images = []
    
    js_text = soup.find_all('script', type='text/javascript')
    for opening in js_text:
        for inner_opening in opening:
            if "jsonp" in inner_opening:
                replacement = inner_opening.replace('/pages/', '/images/').replace('jsonp', 'jpg')
                images.append(replacement)

    if not os.path.exists(title):
        os.makedirs(title)
        
    for image_url in images:
        print(f"Downloading page {train}")
        response = requests.get(image_url, stream=True)
        with open(os.path.join(title, f'pic{train}.jpg'), 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        train += 1

def main():
    parser = argparse.ArgumentParser(description='Download documents from Scribd')
    parser.add_argument('link', help='Link of the Scribd document')
    parser.add_argument('-p', '--images', action='store_true', help='Download images (for PDFs with images)')
    args = parser.parse_args()

    response = requests.get(args.link)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.find('title').get_text()
    clean_title = ''.join(c if c.isalnum() or c.isspace() else '_' for c in title)
    print(clean_title)

    if not args.images:
        extraction = extract_text(soup)
        with open(f'{clean_title}.txt', 'w', encoding='utf-8') as feed:
            feed.write(extraction)
    else:
        download_images(soup, clean_title)


if __name__ == '__main__':
    main()
