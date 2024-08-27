"""
pytest the bucketstore functionality
"""
import bucketstore
import json
import os
import pytest
import sys
import tempfile
from moto import mock_aws


def dbg(text: str) -> None:
    """debug printer for tests"""
    if isinstance(text, dict):
        text = json.dumps(text, sort_keys=True, indent=2)
    caller = sys._getframe(1)
    print("")
    print("----- {} line {} ------".format(caller.f_code.co_name, caller.f_lineno))
    print(text)
    print("-----")
    print("")


def test_login() -> None:
    """
    Ensure that login sets the correct environment variables.

    The ``login`` fixture sets these automatically.
    """
    assert os.environ["AWS_ACCESS_KEY_ID"] == "access_key"
    assert os.environ["AWS_SECRET_ACCESS_KEY"] == "secret_key"
    assert os.environ["AWS_DEFAULT_REGION"] == "us-east-1"


@mock_aws
def test_buckets_can_be_created() -> None:
    bucket = bucketstore.get("test-bucket", create=True)

    assert bucket.name == "test-bucket"
    assert not bucket.is_public  # Buckets are private, by default.
    assert not bucket.all()  # Buckets are empty, by default.
    assert "<S3Bucket" in repr(bucket)


@mock_aws
def test_buckets_are_not_created_automatically() -> None:
    with pytest.raises(ValueError):
        bucketstore.get("non-existent-bucket")


def test_buckets_can_be_listed(bucket: bucketstore.S3Bucket) -> None:
    assert bucket.name in bucketstore.list()


def test_buckets_can_be_deleted(bucket: bucketstore.S3Bucket) -> None:
    bucket["foo"] = "bar"
    bucket.delete()

    # Catching an overly generic exception because boto uses factories to
    # create the exception raised here and thus, isn't importable.
    with pytest.raises(Exception):
        bucket.all()


def test_buckets_can_be_made_public(bucket: bucketstore.S3Bucket) -> None:
    assert not bucket.is_public

    bucket.make_public()
    assert bucket.is_public


def test_buckets_can_set_keys(bucket: bucketstore.S3Bucket) -> None:
    # Buckets can set keys with a function
    bucket.set("foo", "bar")
    assert bucket.get("foo") == b"bar"

    # Keys can also be set via index
    bucket["foo2"] = "bar2"
    assert bucket["foo2"] == b"bar2"


def test_keys_can_be_renamed(bucket: bucketstore.S3Bucket) -> None:
    """test renaming keys"""
    bucket.set("original_name", "value")
    bucket.key("original_name").rename("new_name")
    assert bucket["new_name"] == b"value"

    # check that the original was removed
    assert "original_name" not in bucket


def test_keys_can_be_deleted(bucket: bucketstore.S3Bucket) -> None:
    """test deleting a key"""
    bucket["foo"] = "bar"
    bucket.delete("foo")
    assert not bucket.all()


def test_keys_can_be_made_public(key: bucketstore.S3Key) -> None:
    """make sure keys are private by default, but able to be public"""
    # Keys are private by default.
    assert not key.is_public

    # But they can be made public.
    key.make_public()
    assert key.is_public


def test_keys_can_be_linked_to(key: bucketstore.S3Key) -> None:
    """test that we can link to keys using temp_url and url on public keys"""
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

    # empty response for trying to make a public key public
    assert key.make_public() == {}


def test_keys_have_metadata(key: bucketstore.S3Key) -> None:
    """Metadata is empty by default"""
    assert key.meta == {}

    metadata = {"foo": "bar"}
    key.meta = metadata
    assert key.meta == metadata


def test_keys_have_a_cool_repr(key: bucketstore.S3Key) -> None:
    """The textual representation of the class is nifty, so test it."""
    rep = repr(key)
    assert "S3Key" in rep
    assert key.name in rep
    assert key.bucket.name in rep


def test_private_methods(key: bucketstore.S3Key) -> None:
    """This method contains boto internals, so as long as it returns a truthy value, it is good."""
    assert key._boto_object


def test_bucket_keys_can_be_iterated_upon(bucket: bucketstore.S3Bucket) -> None:
    """Create 10 keys"""
    for index in range(10):
        bucket[str(index)] = str(index)

    keys = bucket.all()
    assert len(keys) == 10

    for index, key in enumerate(keys):
        assert key.name == str(index)


def test_bucket_in_operator(bucket: bucketstore.S3Bucket) -> None:
    """test that we can use the `in` operator on a bucket"""
    for index in range(10):
        bucket[str(index)] = str(index)

    assert "0" in bucket
    assert "10" not in bucket


def test_bucket_del_operator(bucket: bucketstore.S3Bucket) -> None:
    """test that we can use the `del` operator on a bucket + key"""
    for index in range(10):
        bucket[str(index)] = str(index)

    assert "0" in bucket
    del bucket["0"]
    assert "0" not in bucket


def test_key_upload(bucket: bucketstore.S3Bucket) -> None:
    """test that we can use the key upload function"""
    path = "test_upload_file_path"
    # test not a file
    with pytest.raises(Exception):
        bucket.key(path).upload("/this/is/not/a/file")

    # test uploading from a file
    bucket.key(path).upload("LICENSE")
    assert path in bucket
    assert "MIT License" in str(bucket[path])

    # test uploading a file object
    path = "test_upload_file_obj"
    with open("LICENSE", "rb") as temp:
        bucket.key(path).upload(temp)
    assert path in bucket
    assert "MIT License" in str(bucket[path])


def test_key_download(bucket: bucketstore.S3Bucket, key: bucketstore.S3Key) -> None:
    """test that we can use the key download function"""
    # test key doesn't exist
    with pytest.raises(Exception):
        bucket.key("this/is/not/a/key").download("/this/is/not/a/file")

    # test downloading to a file
    _, path = tempfile.mkstemp()
    key.download(path)
    with open(path, "r") as file_0:
        data = file_0.read()
        assert isinstance(data, str)
        assert "a testing value" in data
    os.remove(path)

    # test downloading to a file object
    _, path = tempfile.mkstemp()
    with open(path, "wb") as file_1:
        key.download(file_1)
    with open(path, "r") as file_2:
        data = file_2.read()
        assert isinstance(data, str)
        assert "a testing value" in data
    os.remove(path)


def test_key_size(key: bucketstore.S3Key) -> None:
    """test getting the size of a key"""
    size = key.size()
    assert size
    assert size == 15
    assert size == len(key)
