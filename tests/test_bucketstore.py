"""
pytest the bucketstore functionality
"""
import bucketstore
import json
import os
import pytest
import sys
from moto import mock_s3


def dbg(text):
    """debug printer for tests"""
    if isinstance(text, dict):
        text = json.dumps(text, sort_keys=True, indent=2)
    caller = sys._getframe(1)
    print("")
    print("----- {} line {} ------".format(caller.f_code.co_name, caller.f_lineno))
    print(text)
    print("-----")
    print("")


def test_login():
    """
    Ensure that login sets the correct environment variables.

    The ``login`` fixture sets these automatically.
    """
    assert os.environ["AWS_ACCESS_KEY_ID"] == "access_key"
    assert os.environ["AWS_SECRET_ACCESS_KEY"] == "secret_key"
    assert os.environ["AWS_DEFAULT_REGION"] == "us-east-1"


@mock_s3
def test_buckets_can_be_created():
    bucket = bucketstore.get("test-bucket", create=True)

    assert bucket.name == "test-bucket"
    assert not bucket.is_public  # Buckets are private, by default.
    assert not bucket.all()  # Buckets are empty, by default.
    assert "<S3Bucket" in repr(bucket)


@mock_s3
def test_buckets_are_not_created_automatically():
    with pytest.raises(ValueError):
        bucketstore.get("non-existent-bucket")


def test_buckets_can_be_listed(bucket):
    assert bucket.name in bucketstore.list()


def test_buckets_can_be_deleted(bucket):
    bucket["foo"] = "bar"
    bucket.delete()

    # Catching an overly generic exception because boto uses factories to
    # create the exception raised here and thus, isn't importable.
    with pytest.raises(Exception):
        bucket.all()


def test_buckets_can_be_made_public(bucket):
    assert not bucket.is_public

    bucket.make_public()
    assert bucket.is_public


def test_buckets_can_set_keys(bucket):
    # Buckets can set keys with a function
    bucket.set("foo", "bar")
    assert bucket.get("foo") == b"bar"

    # Keys can also be set via index
    bucket["foo2"] = "bar2"
    assert bucket["foo2"] == b"bar2"


def test_keys_can_be_renamed(bucket):
    bucket.set("original_name", "value")
    bucket.key("original_name").rename("new_name")
    assert bucket["new_name"] == b"value"


def test_keys_can_be_deleted(bucket):
    bucket["foo"] = "bar"
    bucket.delete("foo")
    assert not bucket.all()


def test_keys_can_be_made_public(key):
    # Keys are private by default.
    assert not key.is_public

    # But they can be made public.
    key.make_public()
    assert key.is_public


def test_keys_can_be_linked_to(key):
    # A public link is going to fail because it's private.
    with pytest.raises(ValueError):
        assert key.url

    # A temp link can be generated for private keys.
    temp_url = key.temp_url()
    assert "http" in temp_url
    assert "Expires" in temp_url
    assert "Signature" in temp_url
    assert key.name in temp_url

    # Once it is made public, a URL can be derived from it's elements.
    key.make_public()
    assert "http" in key.url
    assert key.name in key.url


def test_keys_have_metadata(key):
    # Metadata is empty by default
    assert key.meta == {}

    metadata = {"foo": "bar"}
    key.meta = metadata
    assert key.meta == metadata


def test_keys_have_a_cool_repr(key):
    # The textual representation of the class is nifty, so test it.
    rep = repr(key)
    assert "S3Key" in rep
    assert key.name in rep
    assert key.bucket.name in rep


def test_private_methods(key):
    # This method contains boto internals, so as long as it returns a truthy
    # value, it is good.
    assert key._boto_object


def test_bucket_keys_can_be_iterated_upon(bucket):
    # Create 10 keys
    for idx in range(10):
        bucket[str(idx)] = str(idx)

    keys = bucket.all()
    assert len(keys) == 10

    for idx, key in enumerate(keys):
        assert key.name == str(idx)


def test_bucket_in_operator(bucket):
    """test that we can use the in operator on a bucket"""
    for idx in range(10):
        bucket[str(idx)] = str(idx)

    assert "0" in bucket
    assert "10" not in bucket


def test_bucket_del_operator(bucket):
    """test that we can use the del operator on a bucket + key"""
    for idx in range(10):
        bucket[str(idx)] = str(idx)

    assert "0" in bucket
    del bucket["0"]
    assert "0" not in bucket
