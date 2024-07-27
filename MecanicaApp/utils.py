from io import BytesIO

from PIL.Image import Image
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import qrcode
import json
from nacl.secret import SecretBox
from nacl.encoding import Base64Encoder
from pyzbar.pyzbar import decode


def encrypt_serializer_object(obj):
    key = settings.CRYPT_KEY
    crypt_key = SecretBox(key)
    encrypter = crypt_key.encrypt(obj)
    crypt_data = encrypter.ciphertext
    data_base64 = Base64Encoder.encode(crypt_data).decode('utf-8')
    return data_base64


def decrypt_serializer_object(encrypted_data_base64):
    key = settings.CRYPT_KEY
    crypt_key = SecretBox(key)
    encrypted_data = Base64Encoder.decode(encrypted_data_base64.encode('utf-8'))
    decrypted_data = crypt_key.decrypt(encrypted_data)
    return decrypted_data


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


