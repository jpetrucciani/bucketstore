import bucketstore
import pytest
from moto import mock_s3
from typing import Generator


@pytest.fixture(autouse=True)
def login() -> Generator:
    """Fixture that will automatically set the login variables."""
    bucketstore.login("access_key", "secret_key")
    yield


@pytest.fixture
def bucket() -> Generator:
    """
    Fixture that provides a bucketstore bucket.

    Returns:
        bucketstore.S3Bucket: A bucket to work with.
    """
    with mock_s3():
        yield bucketstore.get("bucketstore-playground", create=True)


@pytest.fixture
def key(bucket: bucketstore.S3Bucket) -> bucketstore.S3Key:
    """Fixture that provides a key inside of the given bucket"""
    name = "testing-key"
    bucket.set(name, "a testing value")

    return bucket.key(name)
