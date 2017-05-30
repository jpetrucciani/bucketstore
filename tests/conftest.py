import bucketstore
import pytest

from moto import mock_s3


@pytest.fixture(autouse=True)
def login():
    """Fixture that will automatically set the login variables."""
    bucketstore.login('access_key', 'secret_key')
    yield


@pytest.fixture
def bucket():
    """Fixture that provides a bucketstore bucket.

    Returns:
        bucketstore.S3Bucket: A bucket to work with.

    """
    with mock_s3():
        yield bucketstore.get('bucketstore-playground', create=True)


@pytest.fixture
def key(bucket):
    name = 'testing-key'
    bucket.set(name, 'a testing value')

    return bucket.key(name)
