from utils.logging.loggers import create_rotating_log
from utils.logging.decorators import exception

log_file = "image.log"
logger = create_rotating_log(log_file)

from soap_api import TreoplanSoapApi
from settings import TREOLAN_WDSL_PRODUCT_INFO


@exception(logger)
def main():
    soap_api = TreoplanSoapApi()
    soap_api.wsdl = TREOLAN_WDSL_PRODUCT_INFO
    soap_api.get_client()

    soap_api.save_images()


if __name__ == '__main__':
    """Timeit 655.981519066001"""
    """Crontab: 50 * * * * /path/to/product.py"""
    import timeit
    print(timeit.Timer(main).timeit(number=1))