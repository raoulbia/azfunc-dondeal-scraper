import logging
import azure.functions as func
from scrape_donedeal import *  # Import your scraping function

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        main()  # Call your scraping function
        return func.HttpResponse("Scraping done successfully.", status_code=200)
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        return func.HttpResponse(f"Error: {e}", status_code=500)
