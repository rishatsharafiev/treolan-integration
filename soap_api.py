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

        self.mark_all_as_deleted()
        self.mark_all_as_inactive()
        
        return positions

    def mark_all_as_deleted(self):
        sql_string = "UPDATE treoplan_product SET is_deleted=TRUE;"

        connection = None

        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(sql_string)
                connection.commit()
                return cursor.lastrowid
        finally:
            if connection:
                connection.close()

        return False

    def mark_all_as_inactive(self):
        sql_string = "UPDATE treoplan_product SET is_active=FALSE;"

        connection = None

        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(sql_string)
                connection.commit()
                return cursor.lastrowid
        finally:
            if connection:
                connection.close()

        return False

    def update_or_create(self, cursor, product_dict):
        sql_string = """INSERT INTO treoplan_product(articul, name, id, prid, vendor, currency, freenom, price, is_deleted, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE, TRUE)
        ON DUPLICATE KEY UPDATE
            name = %s,
            id = %s,
            prid = %s,
            vendor = %s,
            currency = %s,
            freenom = %s,
            price = %s,
            is_deleted = FALSE,
            is_active = TRUE;
        """

        prepared_statements = (
            product_dict.get('articul'),
            product_dict.get('name'),
            product_dict.get('id'),
            product_dict.get('prid'),
            product_dict.get('vendor'),
            product_dict.get('currency'),
            product_dict.get('freenom'),
            product_dict.get('price'),
            product_dict.get('name'),
            product_dict.get('id'),
            product_dict.get('prid'),
            product_dict.get('vendor'),
            product_dict.get('currency'),
            product_dict.get('freenom'),
            product_dict.get('price'),
        )

        cursor.execute(sql_string, prepared_statements)

    def batch_update(self, positions):
        sql_string = """INSERT INTO price(article, kod, name, cena, valuta, nalichie, postavchik, img, data_dobavleniya) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE());"""

        connection = None

        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                for position in positions:

                    counter = 0

                    product_dict = {
                        'articul': position.get('articul'),
                        'name': position.get('name'),
                        'id': position.get('id'),
                        'prid': position.get('prid'),
                        'vendor': position.get('vendor'),
                        'currency': position.get('currency'),
                        'freenom': position.get('freenom'),
                        'price': position.get('price'),
                    }
                    self.update_or_create(cursor, product_dict)

                    counter += 1
                    if counter == 10000:
                        connection.commit()
                        counter = 0
                
                if counter != 0:
                    connection.commit()
        finally:
            if connection:
                connection.close()

        return False