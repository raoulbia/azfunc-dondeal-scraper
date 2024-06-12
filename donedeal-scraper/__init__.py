import logging
import azure.functions as func
from scrape_donedeal import scrape_function  # Adjust the import based on your actual function

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Python timer trigger function started.')

    scrape_function()  # Call your scraping function

    logging.info('Python timer trigger function completed.')
