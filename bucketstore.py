"""
bucketstore module
"""
import os
import boto3
import botocore
from typing import List


AWS_DEFAULT_REGION = "us-east-1"


class S3Key(object):
    """An Amazon S3 Key"""

    def __init__(self, bucket: "S3Bucket", name: str) -> None:
        """constructor"""
        super(S3Key, self).__init__()
        self.bucket = bucket
        self.name = name

    def __repr__(self) -> str:
        """str representation of an s3key"""
        return "<S3Key name={0!r} bucket={1!r}>".format(self.name, self.bucket.name)

    @property
    def _boto_object(self):  # type: ignore
        """the underlying boto3 s3 key object"""
        return self.bucket._boto_s3.Object(self.bucket.name, self.name)

    def get(self) -> str:
        """Gets the value of the key."""
        return self._boto_object.get()["Body"].read()

    def set(self, value: str, metadata: dict = None, content_type: str = "") -> dict:
        """Sets the key to the given value."""
        if not metadata:
            metadata = {}
        return self._boto_object.put(
            Body=value, Metadata=metadata, ContentType=content_type
        )

    def rename(self, new_name: str) -> None:
        """Renames the key to a given new name."""
        # Write the new object.
        self.bucket.set(new_name, self.get(), self.meta)

        # Delete the current key.
        self.delete()

        # Set the new name.
        self.name = new_name

    def delete(self,) -> dict:
        """Deletes the key."""
        return self._boto_object.delete()

    @property
    def is_public(self) -> bool:
        """returns True if the public-read ACL is set for the Key."""
        for grant in self._boto_object.Acl().grants:
            if "AllUsers" in grant["Grantee"].get("URI", ""):
                if grant["Permission"] == "READ":
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
            return "{0}/{1}/{2}".format(
                self.bucket._boto_s3.meta.client.meta.endpoint_url,
                self.bucket.name,
                self.name,
            )
        else:
            raise ValueError(
                "{0!r} does not have the public-read ACL set. "
                "Use the make_public() method to allow for "
                "public URL sharing.".format(self.name)
            )

    def temp_url(self, duration: int = 120) -> str:
        """returns a temporary URL for the given key."""
        return self.bucket._boto_s3.meta.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket.name, "Key": self.name},
            ExpiresIn=duration,
        )


class S3Bucket(object):
    """An Amazon S3 Bucket."""

    def __init__(self, name: str, create: bool = False, region: str = "") -> None:
        super(S3Bucket, self).__init__()
        self.name = name
        self.region = region or os.getenv("AWS_DEFAULT_REGION", AWS_DEFAULT_REGION)
        self._boto_s3 = boto3.resource("s3", self.region)
        self._boto_bucket = self._boto_s3.Bucket(self.name)

        # Check if the bucket exists.
        if not self._boto_s3.Bucket(self.name) in self._boto_s3.buckets.all():
            if create:
                # Create the bucket.
                self._boto_s3.create_bucket(Bucket=self.name)
            else:
                raise ValueError("The bucket {0!r} doesn't exist!".format(self.name))

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
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                # The object does not exist.
                return False
            else:
                # Something else has gone wrong.
                raise

    def list(self) -> List:
        """returns a list of keys in the bucket."""
        return [k.key for k in self._boto_bucket.objects.all()]

    @property
    def is_public(self) -> bool:
        """returns True if the public-read ACL is set for the bucket."""
        for grant in self._boto_bucket.Acl().grants:
            if "AllUsers" in grant["Grantee"].get("URI", ""):
                if grant["Permission"] == "READ":
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

    def set(
        self, key: str, value: str, metadata: dict = None, content_type: str = ""
    ) -> dict:
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
        return "<S3Bucket name={0!r}>".format(self.name)


def list() -> List[str]:
    """lists buckets, by name."""
    s3_resource = boto3.resource("s3")
    return [bucket.name for bucket in s3_resource.buckets.all()]


def get(bucket_name: str, create: bool = False) -> S3Bucket:
    """get an s3bucket object by name"""
    return S3Bucket(bucket_name, create=create)


def login(
    access_key_id: str, secret_access_key: str, region: str = AWS_DEFAULT_REGION
) -> None:
    """sets environment variables for boto3."""
    os.environ["AWS_ACCESS_KEY_ID"] = access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret_access_key
    os.environ["AWS_DEFAULT_REGION"] = region
