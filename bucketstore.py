"""
bucketstore module
"""

import io
import os
import os.path
import boto3
import botocore
from typing import BinaryIO, Callable, List, Union


AWS_DEFAULT_REGION = "us-east-1"
__version__ = "VERSION"


class S3Key:
    """An Amazon S3 Key"""

    def __init__(self, bucket: "S3Bucket", name: str) -> None:
        """constructor"""
        super().__init__()
        self.bucket = bucket
        self.name = name

    def __repr__(self) -> str:
        """str representation of an s3key"""
        return f"<S3Key name={self.name} bucket={self.bucket.name}>"

    def __len__(self) -> int:
        """returns the size of the s3 object of this key in bytes"""
        return self.size()

    @property
    def _boto_object(self):  # noqa: ANN202
        """the underlying boto3 s3 key object"""
        return self.bucket._boto_s3.Object(self.bucket.name, self.name)

    def get(self) -> str:
        """Gets the value of the key."""
        return self._boto_object.get()["Body"].read()

    def download(self, file: Union[str, BinaryIO], callback: Callable = None) -> None:
        """download the key to the given path or file object"""
        if self.name not in self.bucket:
            raise Exception("this key does not exist!")

        _download = self.bucket._boto_s3.meta.client.download_fileobj
        if isinstance(file, str):
            with open(file, "wb") as data:
                _download(self.bucket.name, self.name, data, Callback=callback)
        elif isinstance(file, io.IOBase):
            _download(self.bucket.name, self.name, file, Callback=callback)

    def upload(self, file: Union[str, BinaryIO], callback: Callable = None) -> None:
        """upload the file or file obj at the given path to this key"""
        _upload = self.bucket._boto_s3.meta.client.upload_fileobj
        if isinstance(file, str):
            if not os.path.isfile(file):
                raise Exception("file does not exist!")
            with open(file, "rb") as data:
                _upload(data, self.bucket.name, self.name, Callback=callback)
        elif isinstance(file, io.IOBase):
            _upload(file, self.bucket.name, self.name, Callback=callback)

    def size(self) -> int:
        """get the size of this object in s3"""
        total = 0
        for key in self.bucket._boto_bucket.objects.filter(Prefix=self.name):
            total += key.size
        return total

    def set(self, value: str, metadata: dict = None, content_type: str = "") -> dict:
        """Sets the key to the given value."""
        if not metadata:
            metadata = {}
        return self._boto_object.put(Body=value, Metadata=metadata, ContentType=content_type)

    def rename(self, new_name: str) -> None:
        """renames the key to a given new name"""
        # copy the item to avoid pulling and pushing
        self.bucket._boto_s3.Object(self.bucket.name, new_name).copy_from(
            CopySource=f"{self.bucket.name}/{self.name}"
        )
        # Delete the current key.
        self.delete()
        # Set the new name.
        self.name = new_name

    def delete(
        self,
    ) -> dict:
        """Deletes the key."""
        return self._boto_object.delete()

    @property
    def is_public(self) -> bool:
        """returns True if the public-read ACL is set for the Key."""
        for grant in self._boto_object.Acl().grants:
            if "AllUsers" in grant["Grantee"].get("URI", "") and grant["Permission"] == "READ":
                return True

        return False

    def make_public(self) -> dict:
        """sets the 'public-read' ACL for the key."""
        if not self.is_public:
            return self._boto_object.Acl().put(ACL="public-read")
        return {}

    @property
    def meta(self) -> dict:
        """returns the metadata for the key."""
        return self._boto_object.get()["Metadata"]

    @meta.setter
    def meta(self, value: dict) -> None:
        """sets the metadata for the key."""
        self.set(self.get(), value)

    @property
    def url(self) -> str:
        """returns the public URL for the given key."""
        if self.is_public:
            endpoint = self.bucket._boto_s3.meta.client.meta.endpoint_url
            return f"{endpoint}/{self.bucket.name}/{self.name}"
        raise ValueError(
            f"{self.name} does not have the public-read ACL set. "
            "Use the make_public() method to allow for "
            "public URL sharing."
        )

    def temp_url(self, duration: int = 120) -> str:
        """returns a temporary URL for the given key."""
        return self.bucket._boto_s3.meta.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket.name, "Key": self.name},
            ExpiresIn=duration,
        )


class S3Bucket:
    """An Amazon S3 Bucket."""

    def __init__(
        self,
        name: str,
        create: bool = False,
        region: str = "",
        endpoint_url: str = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.region = region or os.getenv("AWS_DEFAULT_REGION", AWS_DEFAULT_REGION)
        env_endpoint_url = os.getenv("AWS_ENDPOINT_URL", "")
        self.endpoint_url = endpoint_url or env_endpoint_url if env_endpoint_url else None
        self._boto_s3 = boto3.resource("s3", self.region, endpoint_url=self.endpoint_url)
        self._boto_bucket = self._boto_s3.Bucket(self.name)

        # Check if the bucket exists.
        if self._boto_s3.Bucket(self.name) not in self._boto_s3.buckets.all():
            if create:
                # Create the bucket.
                self._boto_s3.create_bucket(Bucket=self.name)
            else:
                raise ValueError(f"The bucket {self.name} doesn't exist!")

    def __getitem__(self, key: str) -> str:
        """allows for accessing keys with the array syntax"""
        return self.get(key)

    def __setitem__(self, key: str, value: str) -> dict:
        """allows for setting/uploading keys with the array syntax"""
        return self.set(key, value)

    def __delitem__(self, key: str) -> dict:
        """allow for deletion of keys via the del operator"""
        return self.delete(key)

    def __contains__(self, item: str) -> bool:
        """allows for use of the in keyword on the bucket object"""
        try:
            self._boto_s3.Object(self.name, item).load()
            return True
        except botocore.exceptions.ClientError as exception:
            if exception.response["Error"]["Code"] == "404":
                # The object does not exist.
                return False
            raise  # pragma: no cover

    def list(self, prefix: str = None, legacy_api: bool = False) -> List:
        """returns a list of keys in the bucket."""
        if prefix:
            if legacy_api:
                paginator = self._boto_s3.meta.client.get_paginator("list_objects")
            else:
                paginator = self._boto_s3.meta.client.get_paginator("list_objects_v2")
            objects = []
            for page in paginator.paginate(Bucket=self.name, Prefix=prefix):
                for obj in page.get("Contents", []):
                    objects.append(obj["Key"])
            return objects

        return [k.key for k in self._boto_bucket.objects.all()]

    @property
    def is_public(self) -> bool:
        """returns True if the public-read ACL is set for the bucket."""
        for grant in self._boto_bucket.Acl().grants:
            if "AllUsers" in grant["Grantee"].get("URI", "") and grant["Permission"] == "READ":
                return True

        return False

    def make_public(self) -> dict:
        """Makes the bucket public-readable."""
        return self._boto_bucket.Acl().put(ACL="public-read")

    def key(self, key: str) -> S3Key:
        """returns a given key from the bucket."""
        return S3Key(self, key)

    def all(self) -> List[S3Key]:
        """returns all keys in the bucket."""
        return [self.key(k) for k in self.list()]

    def get(self, key: str) -> str:
        """get the contents of the given key"""
        selected_key = self.key(key)
        return selected_key.get()

    def set(self, key: str, value: str, metadata: dict = None, content_type: str = "") -> dict:
        """creates/edits a key in the s3 bucket"""
        if not metadata:
            metadata = {}
        new_key = self.key(key)
        return new_key.set(value, metadata, content_type)

    def delete(self, key: str = None) -> dict:
        """Deletes the given key, or the whole bucket."""

        # Delete the whole bucket.
        if key is None:
            # Delete everything in the bucket.
            for each_key in self.all():
                each_key.delete()

            # Delete the bucket.
            return self._boto_bucket.delete()

        # If a key was passed, delete they key.
        k = self.key(key)
        return k.delete()

    def __repr__(self) -> str:
        """representation of an s3bucket object"""
        return f"<S3Bucket name={self.name}>"


def list() -> List[str]:  # pylint: disable=redefined-builtin
    """lists buckets, by name."""
    s3_resource = boto3.resource("s3")
    return [bucket.name for bucket in s3_resource.buckets.all()]


def get(bucket_name: str, create: bool = False) -> S3Bucket:
    """get an s3bucket object by name"""
    return S3Bucket(bucket_name, create=create)


def login(
    access_key_id: str,
    secret_access_key: str,
    region: str = AWS_DEFAULT_REGION,
    endpoint_url: str = "",
) -> None:
    """sets environment variables for boto3."""
    os.environ["AWS_ACCESS_KEY_ID"] = access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret_access_key
    os.environ["AWS_DEFAULT_REGION"] = region
    os.environ["AWS_ENDPOINT_URL"] = endpoint_url
