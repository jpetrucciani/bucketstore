BucketStore: A simple Amazon S3 Client, for Python.
===================================================

**BucketStore** is a very simple Amazon S3 client, written in Python. It
aims to be much more straight-forward to use than boto3, and specializes
only in Amazon S3, ignoring the rest of the AWS ecosystem.

Features
--------

- Treats S3 Buckets as Key/Value stores.
- Expects ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY`` to be set.
- Easily make keys (or entire buckets) publically accessable.
- Easily get the public URL for a given key.
- Generates temporary URLs for a given key.

Usage
-----

::

    import bucketstore

    # Create the bucket if it doesn't exist.
    bucket = bucketstore.get('bucketstore-playground', create=True)


::

    # Treat the bucket like a key/value store.
    >>> bucket['foo'] = 'bar'
    >>> bucket['foo']
    bar

    >>> bucket.set('foo2', 'bar2')
    >>> bucket.get('foo2')
    bar2

    >>> bucket.list()
    [u'foo', u'foo2']

    >>> bucket.all()
    [<S3Key bucket='bucketstore-playground' name=u'foo'>, <S3Key bucket='bucketstore-playground' name=u'foo2'>]


::

    >>> bucket.all()[0]
    <S3Key bucket='bucketstore-playground' name=u'foo'>
    >>> foo = _

    >>> foo.set('new value')

    # Generate a temporary share URL.
    >>> foo.temp_url(duration=1200)
    u'https://bucketstore-playground.s3.amazonaws.com/foo?AWSAccessKeyId=AKIAI2RVFNXIW7WS66QQ&Expires=1485493909&Signature=L3gD9avwQZQO1i11dIJXUiZ7Nx8%3D'

    # Make publically accessable.
    >>> foo.make_public()
    >>> foo.url
    'https://s3.amazonaws.com/bucketstore-playground/foo'

    >>> foo.delete()

