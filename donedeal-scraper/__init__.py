import logging
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Your scraping code
    result = "Scraping done"

    return func.HttpResponse(result, status_code=200)
