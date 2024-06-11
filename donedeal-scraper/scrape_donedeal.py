import os
import re
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import urljoin
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Azure credentials and environment configuration
storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')
container_name = os.getenv('CONTAINER_NAME')
parquet_blob_name = os.getenv('PARQUET_BLOB_NAME')
current_date = datetime.now()

def init_webdriver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Error initializing WebDriver: {str(e)}")
        return None
    return driver

def scrape_data(url, xpath):
    driver = init_webdriver()
    if driver is None:
        print("WebDriver not initialized.")
        return pd.DataFrame()  # Return an empty DataFrame if the driver isn't initialized

    try:
        driver.get(url)
    except Exception as e:
        print(f"Error navigating to URL {url}: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame if navigation fails


    page_source = driver.page_source
    driver.quit()

    parser = etree.HTMLParser()
    tree = etree.fromstring(page_source, parser)
    list_items = tree.xpath(xpath)

    ads = []
    for item in list_items:
        ad_url = item.xpath('.//a/@href')[0] if item.xpath('.//a/@href') else None
        ad_text = item.xpath('string(.)').strip() if item.xpath('string(.)') else None
        if ad_url and ad_text:
            ads.append({'text': ad_text, 'url': urljoin(url, ad_url)})
    return pd.DataFrame(ads)

def append_to_parquet(df, filename):
    if not df.empty:
        df.to_csv(filename, mode='a', index=False, header=not os.path.exists(filename))
        df = pd.read_csv(filename)
        df.drop_duplicates(inplace=True)
        df.to_csv(filename, index=False)

        # Handle Azure Blob Storage for Parquet file
        blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net/", credential=storage_account_key)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(parquet_blob_name)

        try:
            stream = BytesIO()
            blob_client.download_blob().download_to_stream(stream)
            stream.seek(0)
            df_existing = pd.read_parquet(stream)
        except Exception as e:
            df_existing = pd.DataFrame()

        df_combined = pd.concat([df_existing, df], ignore_index=True).drop_duplicates()
        output_stream = BytesIO()
        df_combined.to_parquet(output_stream, index=False)
        output_stream.seek(0)
        blob_client.upload_blob(output_stream, overwrite=True)


# Example usage
xpath = "//*[@id='__next']/div[1]/div[4]/div/div/div[2]/ul/li"
page_starts = [0,30,60,90]
for i in page_starts:
    url = f"https://www.donedeal.ie/cars/Audi/A3/Petrol?transmission=Automatic&bodyType=Saloon&year_from=2015&price_from=15000&price_to=25000&mileage_to=100000&engine_from=1400&engine_to=1800&start={i}"
    df_new = scrape_data(url, xpath)
    append_to_parquet(df_new, 'scraped_data.csv')