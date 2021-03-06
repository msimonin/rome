
ROME (Relational Object Mapping Extension)
==========================================

Introduction
------------

ROME (Relational Object Mapping Extension) is an extension for NoQSL
databases, that made them compliant to relational algebra. In short
terms, it enables to use NoSQL databases with an ORM like software, that
is respecting the same interfaces as SQLAlchemy. This document gives
instructions to install/configure/run ROME, and a technical
documentation about how it works.

Installation
------------

Grab the source code
~~~~~~~~~~~~~~~~~~~~

First, execute following the following command in a shell:

::

    git clone https://github.com/badock/rome.git

Python dependencies
~~~~~~~~~~~~~~~~~~~

ROME needs some python dependencies, run the follwing commands in a
shell:

::

    pip install itertools
    pip install sqlalchemy
    pip install riak

Python dependencies
~~~~~~~~~~~~~~~~~~~

The Rome project provides an installation script, which is supposed to
be used like this:

::

    python setup.py install

Running tests (to check if the environment is ready)
----------------------------------------------------

Launch riak (default implementation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Execute the following command in a shell:

::

    riak start

Launch tests
~~~~~~~~~~~~

Execute the following command in a shell:

::

    python execute_tests.py

Documentation
-------------

Integration in OpenStack
~~~~~~~~~~~~~~~~~~~~~~~~

http://dropbox.jonathanpastor.fr/openstack_rome

Folder architecture
~~~~~~~~~~~~~~~~~~~

Detailed project folders architecture:

::

    Rome
    ├── lib ....................................... library files
    │   └── rome ....................................... folder containing ROME files
    │       ├── core ....................................... files of the core of ROME
    │       │   ├── dataformat ....................................... dataformat files (conversion to JSON)
    │       │   └── orm ....................................... object relational mapping files (query)
    │       ├── driver ....................................... folder containing database drivers
    │       │   └── riak ....................................... files related to the RIAK implementation
    │       └── engine ....................................... files used by the ROME engine
    └── test ....................................... files related to testing

Declare an Entity class
~~~~~~~~~~~~~~~~~~~~~~~

To declare an entity class you will have to extend the
lib.rome.core.models.Entity class. In the following example, I create an
entity class that represents Dogs. In the current version, Entity
classes are composed of attributes that follows SQLAlchemy types: this
will be soon replaced by types provided by ROME, however it useful to
garanty some kind of compatibility with SQLAlchemy, thus **easing the
integration of this driver with existing code from Nova controller**.

.. code:: python

    import lib.rome.driver.database_driver as database_driver
    from lib.rome.core.models import Entity
    from lib.rome.core.models import global_scope
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Index, Integer, BigInteger, Enum, String, schema
    from sqlalchemy.dialects.mysql import MEDIUMTEXT
    from sqlalchemy import orm
    from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float
    
    BASE = declarative_base()
    
    @global_scope
    class Dog(BASE, Entity):
        """Represents a dog."""
    
        __tablename__ = 'dogs'
    
        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        specy = Column(String(255))
In order to execute flawlessly the tutorial, please execute the
following code:

.. code:: python

    from lib.rome.core.orm.query import Query
    # Deleting existing dogs to not disturb the tutorial!
    dogs = Query(Dog).all()
    for dog in dogs:
        dog.soft_delete()

.. parsed-literal::

    /Library/Python/2.7/site-packages/riak-2.1.0-py2.7.egg/riak/security.py:32: UserWarning: Found OpenSSL 0.9.8y 5 Feb 2013 version, but expected at least OpenSSL 1.0.1g.  Security may not support TLS 1.2.


Create an entity object and save it in database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Leveraging the class created above, I create a dog called Bobby who is
proud descendant of Griffons. Once bobby is created, I persist it in
database, so that it cannot be forgotten.

.. code:: python

    dogs_model = [{"name": "Bobby", "specy": "Griffon"},
                  {"name": "Rintintin", "specy": "Berger allemand"},
                  {"name": "Snoopy", "specy": "Beagle"}
                 ]
    
    for dog_model in dogs_model:
        # Instanciation of a dog
        dog = Dog()
        # Setting dog's properties
        dog.name = dog_model["name"]
        dog.specy = dog_model["specy"]
        # Saving the dog
        dog.save()

During Bobby's insertion in the database, the ROME driver has outputed
some information about its actions: first an ID has been given to Bobby,
second the data representation (JSON) is displayed. Now that Bobby is in
the database, we would like to find him.

Querying objects
~~~~~~~~~~~~~~~~

Querying of objects follows the same steps as with SQLAlchemy: 1. import
the Query class 2. create a query 3. execute the query

Indeed to find every dogs that are stored in the database:

.. code:: python

    from lib.rome.core.orm.query import Query
    
    # "Select *" query
    dogs = Query(Dog).all()
    print("I may have found some dogs: %s" % (dogs))
    
    # "Count *" query
    dogs_count = Query(Dog).count()
    print("There are %i dog(s) in the database" % (dogs_count))
    
    # "Select * where X and Y" query
    dog = Query(Dog).filter(Dog.name=="Bobby").filter_by(specy="Griffon").first()
    print("I may have found one dog: %s" % (dog))

.. parsed-literal::

    I may have found some dogs: [Lazy(Dog_1:dogs:0), Lazy(Dog_2:dogs:0), Lazy(Dog_3:dogs:-1)]
    There are 3 dog(s) in the database
    I may have found one dog: Lazy(Dog_1:dogs:0)


The previously executed queries returned a list of Lazy(None\_1:dogs:-1)
objects, but no instance of Dog.

.. code:: python

    print("Here are nice dogs with following specs:")
    for dog in dogs:
        print("  * name: %s, specy: %s" % (dog.name, dog.specy))

.. parsed-literal::

    Here are nice dogs with following specs:
      * name: Bobby, specy: Griffon
      * name: Rintintin, specy: Berger allemand
      * name: Snoopy, specy: Beagle


Deleting objects
~~~~~~~~~~~~~~~~

This section will illustrate how an object that has been persisted in
database can be deleted. With the current version of the driver, the
object is not "physically" deleted, but its key is removed from the key
index and made available for reuse. When the key is again used, the
previous object paired with the key will be replaced by this key.

.. code:: python

    from lib.rome.core.orm.query import Query
    
    # Check if Rintintin is in the database
    rintintin_count = Query(Dog).filter(Dog.name=="Rintintin").count()
    print("I have found %i Rintintin(s) in the database" % (rintintin_count))
    
    # Find and Rintintin
    rintintin = Query(Dog).filter(Dog.name=="Rintintin").first()
    rintintin.soft_delete()
    
    # Check if Rintintin is in the database
    rintintin_count = Query(Dog).filter(Dog.name=="Rintintin").count()
    print("I have found %i Rintintin(s) in the database" % (rintintin_count))

.. parsed-literal::

    I have found 1 Rintintin(s) in the database
    I have found 0 Rintintin(s) in the database


Joining tables
~~~~~~~~~~~~~~

To illustrate the joining of tables, let's first create a new table for
species:

.. code:: python

    import lib.rome.driver.database_driver as database_driver
    from lib.rome.core.models import Entity
    from lib.rome.core.models import global_scope
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Index, Integer, BigInteger, Enum, String, schema
    from sqlalchemy.dialects.mysql import MEDIUMTEXT
    from sqlalchemy import orm
    from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float
    
    BASE = declarative_base()
    
    @global_scope
    class Specy(BASE, Entity):
        """Represents a specy."""
    
        __tablename__ = 'species'
    
        id = Column(Integer, primary_key=True)
        name = Column(String(255))
    
    from lib.rome.core.orm.query import Query
    # Deleting existing species to not disturb the tutorial!
    species = Query(Specy).all()
    for specy in species:
        specy.soft_delete()
And let's spawn some species:

.. code:: python

    species_model = [{"name": "Griffon"},
                     {"name": "Berger allemand"},
                     {"name": "Beagle"}
                    ]
    
    for specy_model in species_model:
        # Instanciation of a specy
        specy = Specy()
        # Setting specy's properties
        specy.name = specy_model["name"]
        # Saving the specy
        specy.save()

As the "specy" field in Dog correspond to the "name" field in Dog, let's
try to join the two entity classes on these fields:

.. code:: python

    results = Query(Dog).join(Specy, Specy.name==Dog.specy).all()
    print(results)
    results = Query(Dog, Specy).filter(Specy.name==Dog.specy).all()
    print(results)

.. parsed-literal::

    [[Lazy(Dog_1:dogs:1), Lazy(Specy_1:species:1)], [Lazy(Dog_3:dogs:1), Lazy(Specy_3:species:1)]]
    [[Lazy(Dog_1:dogs:1), Lazy(Specy_1:species:1)], [Lazy(Dog_3:dogs:1), Lazy(Specy_3:species:1)]]


Functions
~~~~~~~~~

As in SQLAlchemy, it is possible to use SQL built in functions. At this
moment only "count" and "sum" are available, however it is possible to
add new functions. Here is an example:

.. code:: python

    from sqlalchemy.sql import func
    
    result = Query(Dog, func.sum(Dog.id), func.count(Dog.id)).all()
    for item in result:
        print(item)

.. parsed-literal::

    [Lazy(Dog_1:dogs:0), 4, 2]
    [Lazy(Dog_3:dogs:0), 4, 2]

