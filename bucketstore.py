import os

import boto3

def list():
    """Lists buckets, by name."""
    return [b.name for b in s3.buckets.all()]

def get(bucket_name, create=False):
    return S3Bucket(bucket_name, create=create)

def login(access_key_id, secret_access_key):
    """Sets environment variables for boto3."""
    os.environ['AWS_ACCESS_KEY_ID'] = access_key_id
    os.environ['AWS_SECRET_ACCESS_KEY'] = secret_access_key



class S3Bucket(object):
    """An Amazon S3 Bucket."""
    def __init__(self, name, create=False):
        super(S3Bucket, self).__init__()
        self.name = name
        self._boto_s3 = boto3.resource('s3')
        self._boto_bucket = self._boto_s3.Bucket(self.name)

        # Check if the bucket exists.
        if not self._boto_s3.Bucket(self.name) in self._boto_s3.buckets.all():
            if create:
                # Create the bucket.
                self._boto_s3.create_bucket(Bucket=self.name)
            else:
                raise ValueError('The bucket {0!r} doesn\'t exist!'.format(self.name))


    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def list(self):
        """Returns a list of keys in the bucket."""
        return [k.key for k in self._boto_bucket.objects.all()]

    def make_public(self):
        """Makes the bucket public-readable."""
        return self._boto_bucket.Acl().put(ACL='public-read')

    def key(self, key):
        """Returns a given key from the bucket."""
        return S3Key(self, key)

    def all(self):
        """Returns all keys in the bucket."""
        return [self.key(k) for k in self.list()]

    def get(self, key):
        k = self.key(key)
        return k.get()

    def set(self, key, value):
        k = self.key(key)
        return k.set(value)

    def delete(self, key=None):
        """Deletes the given key, or the whole bucket."""

        # Delete the whole bucket.
        if key is None:
            # Delete everything in the bucket.
            for key in self._boto_bucket.objects.all():
                key.delete()
            # Delete the bucket.
            self._boto_bucket.delete()

        # If a key was passed, delete they key.
        k = self.key(key)
        return k.delete()

    def __repr__(self):
        return '<S3Bucket name={0!r}>'.format(self.name)


class S3Key(object):
    """An Amazon S3 Key"""
    def __init__(self, bucket, name):
        super(S3Key, self).__init__()
        self.bucket = bucket
        self.name = name

    def __repr__(self):
        return '<S3Key bucket={0!r} name={1!r}>'.format(self.bucket.name, self.name)

    @property
    def _boto_key(self):
        return self.bucket._boto_s3(self.bucket.name, self.name)

    @property
    def _boto_object(self):
        return self.bucket._boto_s3.Object(self.bucket.name, self.name)

    def get(self):
        """Gets the value of the key."""
        return self._boto_object.get()['Body'].read()

    def set(self, value):
        """Sets the key to the given value."""
        return self._boto_object.put(Body=value)

    def rename(self, new_name):
        """Renames the key to a given new name."""
        # Write the new object.
        self.bucket.set(new_name, self.get())

        # Set the new name.
        self.name = new_name

        # Delete the current key.
        self.delete()

    def delete(self):
        """Deletes the key."""
        return self._boto_object.delete()

    def make_public(self):
        """Sets the 'public-read' ACL for the key."""
        # TODO: Doesn't work.
        return self._boto_object.Acl().put(ACL='public-read')

    @property
    def meta(self):
        """Returns the metadata for the key."""
        return self.bucket._boto_s3.Object(self.bucket.name, self.name).get()['Metadata']

    @meta.setter
    def meta(self, value):
        """Sets the metadata for the key."""
        self._boto_object.put(Metadata=value)

    @property
    def url(self):
        """Returns the public URL for the given key."""
        return '{0}/{1}/{2}'.format(self.bucket._boto_s3.meta.client.meta.endpoint_url, self.bucket.name, self.name)

    def temp_url(self, duration=120):
        """Rerturns a temporary URL for the given key."""
        return self.bucket._boto_s3.meta.client.generate_presigned_url('get_object', Params={'Bucket': self.bucket.name, 'Key': self.name}, ExpiresIn=duration)
