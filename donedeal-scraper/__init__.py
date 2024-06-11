import logging

from azure.functions import TimerRequest
from datetime import datetime, timezone
from .scrape_donedeal import *


def main(mytimer: TimerRequest) -> None:
    utc_timestamp = datetime.now().replace(tzinfo=timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
