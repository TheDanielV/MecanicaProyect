from io import BytesIO

from PIL.Image import Image
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import qrcode
import json

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import logging

from django.template.loader import render_to_string
from nacl.secret import SecretBox
from nacl.encoding import Base64Encoder

from PIL import Image
from pyzbar.pyzbar import decode

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import base64
import os
from django.conf import settings


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


def get_key(password, salt, key_length=32):
    """
    Deriva una clave del password y salt dados.
    """
    backend = default_backend()
    kdf = Scrypt(
        salt=salt,
        length=key_length,  # 32 bytes for key
        n=2 ** 14,
        r=8,
        p=1,
        backend=backend
    )
    key = kdf.derive(password)
    return key


def encrypt_data(data):
    """
    Encripta datos utilizando AES-256 en modo GCM.

    Args:
        data (str): El dato que se desea encriptar.

    Returns:
        str: El dato encriptado codificado en base64.
    """
    password = settings.CRYPT_KEY
    salt = os.urandom(16)
    key = get_key(password, salt)

    iv = os.urandom(12)  # IV de 12 bytes para GCM

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data.encode('utf-8')) + padder.finalize()

    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_data = base64.b64encode(salt + iv + encryptor.tag + encrypted).decode('utf-8')
    return encrypted_data


def decrypt_data(encrypted_data_base64):
    """
    Desencripta datos que han sido encriptados y codificados en base64.

    Args:
        encrypted_data_base64 (str): El dato encriptado y codificado en base64.

    Returns:
        str: El dato desencriptado.
    """
    password = settings.CRYPT_KEY
    encrypted_data = base64.b64decode(encrypted_data_base64.encode('utf-8'))

    salt = encrypted_data[:16]
    iv = encrypted_data[16:28]  # IV de 12 bytes
    tag = encrypted_data[28:44]
    ciphertext = encrypted_data[44:]

    key = get_key(password, salt)

    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return data.decode('utf-8')


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


def send_credentias_email(user_email, user, password):
    subject = 'Credenciales de acceso'
    message = f'Tu Usuario es: {user} y tu contraseña es: {password}'

    template = render_to_string('email.html', {
        'message': message
    })

    email = EmailMessage(
        subject,
        template,
        from_email=settings.EMAIL_HOST_USER,
        to=[user_email]
    )
    email.fail_silently = False

    try:
        email.send()
        return True
    except Exception as e:
        print(e)
        return False
