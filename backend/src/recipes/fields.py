import base64
import imghdr
import mimetypes
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and 'data:' in data and ';base64,' in data:
            header, data = data.split(';base64,')
            mime_type = header.split(':')[-1]
            extension = mimetypes.guess_extension(mime_type)

            if extension not in ['.jpg', '.jpeg', '.png', '.bmp']:
                raise serializers.ValidationError('Invalid image type.')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = self.get_file_name(decoded_file)
            data = ContentFile(decoded_file, name=f'{file_name}{extension}')

        return super().to_internal_value(data)

    def get_file_name(self, decoded_file, length=12):
        file_name = str(uuid.uuid4())[:length]
        file_extension = self.get_file_extension(file_name, decoded_file)
        return f'{file_name}.{file_extension}'

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        return "jpg" if extension == "jpeg" else extension
