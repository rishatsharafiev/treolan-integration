#!/usr/bin/env python3
import math
import pydash
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.helpers import serialize_object
from collections import OrderedDict
from lxml import etree
# imports
import settings
from utils.db import get_connection
import time
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
        transport = Transport(timeout=150, operation_timeout=150)
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

    def get_image(self, articul):
        params = {
            'Login': self.login,
            'password': self.password,
            'Articul': articul,
        }

        response = self.client.service.ProductInfoV2(**params)
        pictures = response.findall('.//PictureLink/row')
        pictures = list(filter(lambda picture: picture.get('ImageSize') == 'bigimage', pictures))

        try:
            return pictures[0].get('Link')
        except IndexError:
            return ''

    def save_images(self):
        articuls = self.get_products_without_images()

        for articul in articuls:
            url = self.get_image(articul)
            self.create_image(articul, url)
            time.sleep(0.01)

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

    def get_products_without_images(self, limit=1000):
        sql_string = """SELECT `treoplan_product`.`articul` FROM `treoplan_product` 
            LEFT JOIN `treoplan_image` ON `treoplan_product`.`articul` = `treoplan_image`.`articul` 
            WHERE `treoplan_image`.`url` IS NULL LIMIT %s;"""
        
        prepared_statements = (
            limit,
        )

        connection = None

        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(sql_string, prepared_statements)
                products = cursor.fetchall()

                return [product[0] for product in products]
        finally:
            if connection:
                connection.close()

        return False

    def create_image(self, articul: str, url: str):
        sql_string = "INSERT INTO treoplan_image(url, articul) VALUES (%s, %s);"

        prepared_statements = (
            url,
            articul,
        )

        connection = None

        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(sql_string, prepared_statements)
                connection.commit()
                return cursor.lastrowid
        finally:
            if connection:
                connection.close()

        return False


    def get_active_products_count(self):
        sql_string = """SELECT COUNT(*) FROM `treoplan_product`
            WHERE `treoplan_product`.`is_deleted`=FALSE 
                AND `treoplan_product`.`is_active`=TRUE;
        """
        
        connection = None

        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(sql_string)
                result = cursor.fetchone()

                return pydash.get(result, '0', 0)
        finally:
            if connection:
                connection.close()

        return False

    def get_active_products(self, limit=1000, offset=0):
        sql_string = """SELECT tp.articul, tp.prid, tp.currency, tp.name, tp.price, tp.freenom, ti.url
            FROM treoplan_product tp
            LEFT JOIN (
                SELECT url, articul
                FROM treoplan_image
                WHERE id IN (
                SELECT min(id) 
                FROM treoplan_image
                GROUP BY articul
                )
            ) ti ON tp.articul =  ti.articul
            WHERE tp.is_deleted=FALSE AND tp.is_active=TRUE
            LIMIT %s
            OFFSET %s;"""
        
        prepared_statements = (
            limit,
            offset,
        )

        connection = None

        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(sql_string, prepared_statements)
                products = cursor.fetchall()

                return [{
                    'articul': product[0], 
                    'prid': product[1],
                    'currency': product[2],
                    'name': product[3],
                    'price': product[4] if product[4] else 0,
                    'freenom': product[5] if product[5] else '',
                    'url': product[6] if product[6] else '',
                } for product in products]
        finally:
            if connection:
                connection.close()

        return False

    def clear_price_by_supplier(self, supplier: str = 'ТРЕОЛАН'):
        sql_string = """DELETE FROM `price` WHERE postavchik=%s;"""
        
        prepared_statements = (
            supplier,
        )

        connection = None

        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(sql_string, prepared_statements)
                connection.commit()
                return cursor.lastrowid
        finally:
            if connection:
                connection.close()

        return False

    def create_prices(self, prices):
        sql_string = """INSERT INTO price(article, kod, name, cena, valuta, nalichie, postavchik, img, data_dobavleniya) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE());"""

        connection = None

        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                for price in prices:

                    counter = 0

                    prepared_statements = (
                        price.get('article'),
                        price.get('kod'),
                        price.get('name'),
                        price.get('cena'),
                        price.get('valuta'),
                        price.get('nalichie'),
                        price.get('postavchik'),
                        price.get('img'),
                    )

                    cursor.execute(sql_string, prepared_statements)

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

    def save_prices(self):
        # clear by supplier
        self.clear_price_by_supplier(supplier='ТРЕОЛАН')

        # get products count
        products_count = self.get_active_products_count()

        # get products list
        offset = 0
        limit = 10000
        steps = math.ceil(products_count / limit)

        for step in range(steps):
            offset = limit*step
            product_list = self.get_active_products(limit=limit, offset=offset)

            price_list = [{
                'article': product_dict.get('articul'), 
                'kod': product_dict.get('prid'), 
                'name': product_dict.get('name'), 
                'cena': product_dict.get('price'), 
                'valuta': product_dict.get('currency'), 
                'nalichie': product_dict.get('freenom'), 
                'postavchik': 'ТРЕОЛАН', 
                'img': product_dict.get('url'), 
             } for product_dict in product_list]

            # create
            self.create_prices(prices=price_list)