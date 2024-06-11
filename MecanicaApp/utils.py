import base64
import os
from io import BytesIO
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import qrcode
import json
from nacl.secret import SecretBox
from nacl.encoding import Base64Encoder


def encrypt_serializer_object(obj):
    key = b'\xc95\x8a\x92\xf0\x1e,\xb4\r\xbf\xc2I\x8fv\x00\xd6\xca\xcc\x9f\xaa\x03\xc8\x83\xdc\x90\x81X^8u\x8d\xd2'
    crypt_key = SecretBox(key)
    encrypter = crypt_key.encrypt(obj)
    crypt_data = encrypter.ciphertext
    data_base64 = Base64Encoder.encode(crypt_data).decode('utf-8')
    return data_base64


def serialize_object(obj):
    obj_dict = model_to_dict(obj)
    return json.dumps(obj_dict, cls=DjangoJSONEncoder).encode('utf-8')


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    byte_io = BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io
