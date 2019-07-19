BucketStore: A simple Amazon S3 Client, for Python.
===================================================

.. image:: https://travis-ci.org/jpetrucciani/bucketstore.svg?branch=master
    :target: https://travis-ci.org/jpetrucciani/bucketstore


.. image:: https://badge.fury.io/py/bucketstore.svg
   :target: https://badge.fury.io/py/bucketstore
   :alt: PyPI version


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Code style: black


.. image:: https://img.shields.io/badge/python-3.5+-blue.svg
   :target: https://www.python.org/downloads/release/python-350/
   :alt: Python 3.5+ supported


**BucketStore** is a very simple Amazon S3 client, written in Python. It
aims to be much more straight-forward to use than boto3, and specializes
only in Amazon S3, ignoring the rest of the AWS ecosystem.


Features
--------

- Treats S3 Buckets as Key/Value stores.
- Automatic support for ``AWS_ACCESS_KEY_ID``, ``AWS_SECRET_ACCESS_KEY``, and ``AWS_DEFAULT_REGION`` environment variables.
- Easily make keys (or entire buckets) publically accessable.
- Easily get the public URL for a given key.
- Generates temporary URLs for a given key.
- Use S3 in a pythonic way!

Usage
-----

Installation
^^^^^^^^^^^^

::

    $ pip install bucketstore

Get (or create) a bucket, easily:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import bucketstore

    # Create the bucket if it doesn't exist.
    bucket = bucketstore.get('bucketstore-playground', create=True)


Treat the bucket like a key/value store:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: pycon

    >>> bucket
    <S3Bucket name='bucketstore-playground'>

    # get/set using array syntax
    >>> bucket['foo'] = 'bar'
    >>> bucket['foo']
    bar

    # get/set using methods
    >>> bucket.set('foo2', 'bar2')
    >>> bucket.get('foo2')
    bar2

    # list keys
    >>> bucket.list()
    [u'foo', u'foo2']

    # all keys
    >>> bucket.all()
    [<S3Key name=u'foo' bucket='bucketstore-playground'>, <S3Key name=u'foo2' bucket='bucketstore-playground'>]

    # check if a key exists in the bucket
    >>> 'foo' in bucket
    True

    # delete keys in the bucket
    >>> del bucket['foo2']
    {}


Interact with S3 keys:
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: pycon

    >>> bucket.key('foo')
    <S3Key bucket='bucketstore-playground' name=u'foo'>

    >>> foo = _
    >>> foo.set('new value')

    # Generate a temporary share URL.
    >>> foo.temp_url(duration=1200)
    u'https://bucketstore-playground.s3.amazonaws.com/foo?AWSAccessKeyId=AKIAI2RVFNXIW7WS66QQ&Expires=1485493909&Signature=L3gD9avwQZQO1i11dIJXUiZ7Nx8%3D'

    # Make key publically accessable.
    >>> foo.make_public()
    >>> foo.url
    'https://s3.amazonaws.com/bucketstore-playground/foo'

    # Get / set metadata for key.
    >>> foo.meta = {'foo': 'bar'}
    >>> foo.meta
    {'foo': 'bar}

    # Rename key to 'foo3'.
    >>> foo.rename('foo3')

    # Delete the key.
    >>> foo.delete()

    # Create a key with metadata at the same time.
    >>> foo = bucket.key('foo.html')
    >>> foo.set('<h1>bar</h1>', {'content_type': 'text/html'})

Other methods include ``bucketstore.login(access_key_id, secret_access_key)``, ``bucketstore.list()``, and ``bucketstore.get(bucket_name, create=False)``.

Tests
-----

Tests are run through Tox_.

.. code-block:: shell

    # Run tests against all environments.
    $ tox
    # Run against a specific version.
    $ tox -e py35
    # Run with pytest arguments.
    $ tox -- --pdb

.. _Tox: https://tox.readthedocs.io/en/latest/


✨🍰✨
