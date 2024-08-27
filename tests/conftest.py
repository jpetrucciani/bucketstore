"""
bucketstore pytest configuration
"""

import bucketstore
import os
import pytest
from moto import mock_aws
from typing import Generator


# this is to attempt to hack our way around boto issues
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(autouse=True)
def login() -> Generator:  # noqa: PT004
    """fixture that will automatically set the login variables."""
    bucketstore.login("access_key", "secret_key")
    return


@pytest.fixture
def bucket() -> Generator:
    """fixture that provides a bucketstore bucket."""
    with mock_aws():
        yield bucketstore.get("bucketstore-playground", create=True)


@pytest.fixture
def key(bucket: bucketstore.S3Bucket) -> bucketstore.S3Key:
    """fixture that provides a key inside of the given bucket"""
    name = "testing-key"
    bucket.set(name, "a testing value")

    return bucket.key(name)
