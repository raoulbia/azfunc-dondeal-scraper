import os, re, csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import urljoin

# Assuming current_date is defined somewhere in the script
current_date = datetime.now()

def import_xml_with_selenium(url, xpath):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--user-agent=Mozilla/5.0')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get(url)
    driver.implicitly_wait(10)

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
            ad_full_url = urljoin(url, ad_url)
            ads.append((ad_text, ad_full_url))

    return ads

def extract_info(title):
    patterns = {
        "description": r"\d{1,2}.*",
        "engine": r"\d\.\d [A-Za-z]+",
        "mileage": r"\d{1,3}(,\d{3})* (mi|km)",
        "price": r"€\d{1,3}(,\d{3})*",
        "on_sale_since": r"\d+ (day|days|hour|hours)",
        "greenlight": "Greenlight",
        "dealer_name": r"^[\w\s']+ Dealer"
    }
    info = {}
    for key, pattern in patterns.items():
        if key == "greenlight":
            info[key] = "yes" if "Greenlight" in title else "no"
        else:
            try:
                info[key] = re.search(pattern, title).group(0)
            except:
                info[key] = None
    return info

def calculate_sale_date(row):
    if pd.isnull(row):
        return None
    try:
        quantity, unit = re.search(r"(\d+) (day|days|hour|hours)", row).groups()
        quantity = int(quantity)
        sale_date = current_date - timedelta(days=quantity) if 'day' in unit else current_date - timedelta(hours=quantity)
        return sale_date.strftime('%Y-%m-%d')
    except AttributeError:
        return None

def convert_value(value):
    match = re.search(r'(\d+(,\d{3})*(\.\d+)?)\s*(mi|km)', str(value), re.IGNORECASE)
    if match:
        number, _, _, unit = match.groups()
        number = float(number.replace(',', ''))
        return round(number * 1.60934, 2) if 'mi' in unit.lower() else number
    else:
        return None

def append_to_csv(df, filename):
    file_path = os.path.join('outputs', filename)
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        df.to_csv(file, header=not file_exists, index=False)

# Example usage
xpath = "//*[@id='__next']/div[1]/div[4]/div/div/div[2]/ul/li"
page_starts = [0,30,60,90]
for i in page_starts:
    url = f"https://www.donedeal.ie/cars/Audi/A3/Petrol?transmission=Automatic&bodyType=Saloon&year_from=2015&price_from=15000&price_to=25000&mileage_to=100000&engine_from=1400&engine_to=1800&start={i}"
    data = import_xml_with_selenium(url, xpath)

    # Convert to DataFrame
    columns = ['Ad Text', 'URL']  # Adjust column names as necessary
    df = pd.DataFrame(data, columns=columns)

    # Drop rows where any field is not populated
    df.dropna(how='any', inplace=True)

    # Assuming you have a function to extract and add more detailed info from 'Ad Text'
    # You would process 'df' here to split 'Ad Text' into more columns, then drop incomplete rows again if necessary

    # Finally, ensure URL is the last column if it got moved during processing
    # This step is only necessary if additional columns were added in between
    cleaned_car_sales_df = df[[col for col in df.columns if col != 'URL'] + ['URL']]

    # The 'Title' column was referenced but not defined in the DataFrame. Assuming 'Ad Text' should be used.
    extracted_info = cleaned_car_sales_df['Ad Text'].apply(lambda x: pd.Series(extract_info(x)))
    info_df = pd.concat([cleaned_car_sales_df.drop(columns=['Ad Text']), extracted_info], axis=1)
    info_df['on_sale_since_v2'] = info_df['on_sale_since'].apply(calculate_sale_date)
    info_df['mileage'] = info_df['mileage'].apply(convert_value)


    # Reorder columns to ensure URL is the last column
    columns_order = [col for col in info_df.columns if col != 'URL'] + ['URL']
    info_df = info_df[columns_order]
    info_df['description'] = 'Audi A3'
    info_df.rename(columns={'description': 'model', 'mileage': 'km'}, inplace=True)
    info_df.dropna(how='any', inplace=True)
    print(info_df.head())
    print(info_df.shape)
    append_to_csv(info_df, 'car_sales_info.csv')

# After appending to CSV, read the file, deduplicate, and save again
def deduplicate_csv(filename):
    file_path = os.path.join('outputs', filename)
    df = pd.read_csv(file_path)
    # Drop duplicates based on all columns except 'on_sale_since', 'on_sale_since_v2', and 'URL'
    columns_for_deduplication = [col for col in df.columns if col not in ['on_sale_since', 'on_sale_since_v2', 'URL']]
    df_deduped = df.drop_duplicates(subset=columns_for_deduplication, keep='last')
    print(df_deduped.shape)
    df_deduped.to_csv(file_path, index=False, encoding='utf-8')

# Call the deduplicate function after appending to CSV
deduplicate_csv('car_sales_info.csv')