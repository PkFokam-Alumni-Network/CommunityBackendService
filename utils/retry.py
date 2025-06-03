from sqlalchemy.exc import OperationalError
from tenacity import retry, stop_after_attempt, wait_exponential
import tenacity

def retry_on_db_error():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=tenacity.retry_if_exception_type(OperationalError)
    ) 