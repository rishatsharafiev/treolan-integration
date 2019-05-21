#!/usr/bin/env python3

from zeep import Client, Settings
from zeep.transports import Transport
from zeep.helpers import serialize_object
from collections import OrderedDict
from lxml import etree
# imports
import settings
from utils.db import get_connection

# logging
# import logging.config
# logging.config.dictConfig({
#     'version': 1,
#     'formatters': {
#         'verbose': {
#             'format': '%(name)s: %(message)s'
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': settings.DEBUG_LEVEL,
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose',
#         },
#     },
#     'loggers': {
#         'zeep.transports': {
#             'level': settings.DEBUG_LEVEL,
#             'propagate': True,
#             'handlers': ['console'],
#         },
#     }
# })

class TreoplanSoapApi:
    wsdl = settings.TREOLAN_WDSL
    login = settings.TREOLAN_LOGIN
    password = settings.TREOLAN_PASSWORD

    def get_client(self):
        transport = Transport(timeout=120, operation_timeout=120)
        settings = Settings(strict=False, xml_huge_tree=True)
        self.client = Client(self.wsdl, transport=transport, settings=settings)

        return True


    def listRecursive(self, d, key):
        for k, v in d.items ():
            if isinstance (v, OrderedDict):
                for found in listRecursive (v, key):
                    yield found
            if k == key:
                yield v

    def get_products(self):
        params = {
            'login': self.login,
            'password': self.password,
            'category': '',
            'vendorid': 0,
            'keywords': '',
            'criterion': 0,
            'inArticul': 0,
            'inName': 0,
            'inMark': 0,
            'showNc': 1,
        }

        response = self.client.service.GenCatalogV2(**params)
        result = response['Result']
        root = etree.fromstring(result)
        positions = root.findall('.//position')

        for position in positions[:10]:
            print(position.get('articul'))

        # for position in self.listRecursive(serialize_object(result), 'position'):
        #     print(position)
        
        return True
