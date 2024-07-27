from io import BytesIO

from PIL.Image import Image
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import qrcode
import json
from nacl.secret import SecretBox
from nacl.encoding import Base64Encoder

from PIL import Image
from pyzbar.pyzbar import decode


def encrypt_serializer_object(obj):
    """
    Encripta un objeto serializado utilizando una clave secreta.

    Args:
        obj (bytes): El objeto serializado que se desea encriptar.

    Returns:
        str: El objeto encriptado codificado en base64.
    """
    key = settings.CRYPT_KEY
    crypt_key = SecretBox(key)
    encrypter = crypt_key.encrypt(obj)
    crypt_data = encrypter.ciphertext
    data_base64 = Base64Encoder.encode(crypt_data).decode('utf-8')
    return data_base64


def decrypt_serializer_object(encrypted_data_base64):
    """
    Desencripta un objeto serializado que ha sido encriptado y codificado en base64.

    Args:
        encrypted_data_base64 (str): El objeto encriptado y codificado en base64.

    Returns:
        bytes: El objeto desencriptado.
    """
    key = settings.CRYPT_KEY
    crypt_key = SecretBox(key)
    encrypted_data = Base64Encoder.decode(encrypted_data_base64.encode('utf-8'))
    decrypted_data = crypt_key.decrypt(encrypted_data)
    return decrypted_data


def serialize_object(obj):
    """
    Serializa un objeto de Django en formato JSON.

    Args:
        obj (Model): El objeto de Django que se desea serializar.

    Returns:
        bytes: La representación del objeto en formato JSON codificada en UTF-8.
    """
    obj_dict = model_to_dict(obj)
    return json.dumps(obj_dict, cls=DjangoJSONEncoder).encode('utf-8')


def generate_qr_code(data):
    """
    Genera un código QR a partir de los datos proporcionados.

    Args:
        data (str): Los datos que se desean codificar en el código QR.

    Returns:
        BytesIO: Un objeto de BytesIO que contiene la imagen del código QR en formato PNG.
    """
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


def read_qr_code(image):
    """
    Lee el contenido de un código QR desde una imagen.

    Args:
        image (InMemoryUploadedFile): La imagen subida que contiene el QR.

    Returns:
        list: Una lista con el contenido de los códigos QR encontrados.
    """
    img = Image.open(image)
    decoded_objects = decode(img)
    qr_content = [obj.data.decode('utf-8') for obj in decoded_objects]
    return qr_content
