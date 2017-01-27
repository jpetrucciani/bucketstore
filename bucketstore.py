import os

import boto3




def list():
    """Lists buckets, by name."""
    return [b.name for b in s3.buckets.all()]

def new(bucket_name):
    """Creates a new bucket, and returns it."""
    pass

def get(bucket_name):
    return S3Bucket(bucket_name)

def login(access_key_id, secret_access_key):
    os.environ['AWS_ACCESS_KEY_ID'] = access_key_id
    os.environ['AWS_SECRET_ACCESS_KEY'] = access_key_id


class S3Bucket(object):
    """An Amazon S3 Bucket."""
    def __init__(self, name, create=False):
        super(S3Bucket, self).__init__()
        self.name = name

        if not create:
            pass
        # Ensure exists, or create.

    @property
    def _boto_s3(self):
        return boto3.resource('s3')

    @property
    def _boto_bucket(self):
        return self._boto_s3.Bucket(self.name)

    def __getitem__(self, key):
        # return self._boto_bucket.objects[key]
        return self.get(key)

    def list(self):
        """Returns a list of keys in the bucket."""
        return [k.key for k in self._boto_bucket.objects.all()]

    def make_public(self):
        return self._boto_bucket.set_acl('public-read')

    def key(self, key):
        return S3Key(self, key)

    def get(self, key):
        k = self.key(key)
        return k.get()

    def set(self, key, value):
        k = self.key(key)
        return k.set(value)

    def delete(self, key):
        #
        pass

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

    def get(self):
        return self.bucket._boto_s3.Object(self.bucket.name, self.name).get()['Body'].read()

    def set(self, value):
        return self.bucket._boto_s3(self.bucket.name, self.name).put(Body=value)

    def delete(self):
        return self.bucket._boto_s3(self.bucket.name, self.name).delete()

    def make_public(self):
        self.bucket._boto_bucket.lookup(self.name).set_acl('public-read')

    @property
    def url(self):
        return '{0}/{1}/{2}'.format(self.bucket._boto_s3.meta.client.meta.endpoint_url, self.bucket.name, self.name)
