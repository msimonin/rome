from lib.rome.core.orm.query import Query
from lib.rome.core.orm.query import Function
from _fixtures import *

import unittest

import lib.rome.driver.database_driver as database_driver
from lib.rome.core.models import Entity
from lib.rome.core.models import global_scope
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Index, Integer, BigInteger, Enum, String, schema
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy import orm
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float
import logging
from lib.rome.core.models import get_model_class_from_name
BASE = declarative_base()

from lib.rome.utils.SecondaryIndexDecorator import secondary_index_decorator

@global_scope
@secondary_index_decorator("name")
@secondary_index_decorator("specy")
class Dog(BASE, Entity):
    """Represents a dog."""

    __tablename__ = 'dogs'

    id = Column(Integer, primary_key=True)

    name = Column(String(255))
    specy = Column(String(255))

@global_scope
class Specy(BASE, Entity):
    """Represents a specy."""

    __tablename__ = 'species'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class TestDogs(unittest.TestCase):
    def test_creation(self):
        logging.getLogger().setLevel(logging.DEBUG)
        bobby = Dog()
        bobby.name = "Bobby"
        bobby.specy = "Griffon"
        bobby.save()
        specy = Specy()
        specy.name = "Griffon"
        specy.save()
        self.assertEqual(True, True)

        from lib.rome.core.dataformat import get_encoder
        from lib.rome.core.lazy import LazyValue
        converter = get_encoder()
        bobby_dict = converter.simplify(bobby)
        toto = converter.simplify(LazyValue(bobby_dict, None))
        print(toto)

    def test_selection(self):
        logging.getLogger().setLevel(logging.DEBUG)
        query = Query(Dog).filter(Dog.name=="Bobby").filter(Dog.specy=="Griffon")
        bobby = query.first()
        bobby.save()
        print("My dog's name is %s" % (bobby.name))
        self.assertEqual(True, True)

    def test_join(self):
        # First way to make a join
        items = Query(Dog, func.sum(Dog.id)).join(Specy, Specy.name==Dog.specy).all()
        for item in items:
            print("%s" % (item))
        # Second way to make a join
        items = Query(Dog, Specy).filter(Specy.name==Dog.specy).all()
        for item in items:
            print("%s" % (item))


if __name__ == '__main__':
    erase_fixture_data()
    initialise_fixture_data()
    unittest.main()
