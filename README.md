[![PyPI version](https://badge.fury.io/py/bucketstore.svg)](https://badge.fury.io/py/bucketstore)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Python 3.6+ supported](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)

**bucketstore** is a very simple Amazon S3 client, written in Python. It
aims to be much more straight-forward to use than boto3, and specializes
only in Amazon S3, ignoring the rest of the AWS ecosystem.

# Features

- Treats S3 Buckets as Key/Value stores.
- Automatic support for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
  and `AWS_DEFAULT_REGION` environment variables.
- Easily make keys (or entire buckets) publically accessable.
- Easily get the public URL for a given key.
- Generates temporary URLs for a given key.
- Use S3 in a pythonic way\!

# Usage

## Installation

```bash
pip install bucketstore
```

## Get (or create) a bucket, easily:

```python
import bucketstore

# Create the bucket if it doesn't exist.
bucket = bucketstore.get('bucketstore-playground', create=True)
```

## Treat the bucket like a key/value store:

```pycon
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
```

## Interact with S3 keys:

```pycon
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

# Create a key with a content type
>>> foo = bucket.key('foo.html')
>>> foo.set('<h1>bar</h1>', content_type='text/html')

# upload to key
>>> bucket.key('test.py').upload('/tmp/test.py')

# or upload with a file-like object! (make sure it's open in binary mode)
>>> with open('/tmp/test.py', 'rb') as file:
>>>     bucket.key('test.py').upload(file)

# download to file
>>> bucket.key('test.py').download('/tmp/test.py')

# or download to a file-like object! (make sure it's open in binary mode)
>>> with open('/tmp/test.py', 'wb') as file:
>>>     bucket.key('test.py').download(file)

# size of key
>>> bucket.key('test.py').size()
>>> len(bucket.key('test.py'))
15
```

Other methods include `bucketstore.login(access_key_id, secret_access_key)`, `bucketstore.list()`, and
`bucketstore.get(bucket_name, create=False)`.

# Tests

Tests are run through [Tox](https://tox.readthedocs.io/en/latest/).

```shell
# Run tests against all environments.
$ tox
# Run against a specific version.
$ tox -e py310
# Run with pytest arguments.
$ tox -- --pdb
```

✨🍰✨
