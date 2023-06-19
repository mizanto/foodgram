import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            if 'data:' in data and ';base64,' in data:
                _, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            data = ContentFile(
                decoded_file, name=self.get_file_name(decoded_file))
        return super().to_internal_value(data)

    def get_file_name(self, decoded_file, length=12):
        file_name = str(uuid.uuid4())[:length]
        file_extension = self.get_file_extension(file_name, decoded_file)
        return f'{file_name}.{file_extension}'

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        return "jpg" if extension == "jpeg" else extension
