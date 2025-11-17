"""The module providing database security."""

from base64 import b64decode, b64encode
from os import urandom
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..errors import IncorrectError

KDF_ITERATIONS = 600_000
SALT_SIZE = 16
IV_SIZE = 12
TAG_SIZE = 16
KEY_LENGTH = 32


def file_to_bytes(path: str | Path, password: str) -> bytes:
    """Read a file at `path` and attempt decryption with `password`, decoding from base64.

    Args:
        path: The path to the file, in `str` or `pathlib.Path`
        password: The password to the file, in `str`, key derived in-function

    Returns:
        A `bytes` object containing the decrypted data.

    Raises:
        IncorrectError: The supplied password is wrong.
    """
    data = b64decode(Path(path).read_bytes())

    salt = data[:SALT_SIZE]
    iv = data[SALT_SIZE : SALT_SIZE + IV_SIZE]
    tag = data[SALT_SIZE + IV_SIZE : SALT_SIZE + IV_SIZE + TAG_SIZE]
    ciphertext = data[SALT_SIZE + IV_SIZE + TAG_SIZE :]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=KDF_ITERATIONS,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode())

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()

    try:
        return decryptor.update(ciphertext) + decryptor.finalize()
    except InvalidTag as e:
        raise IncorrectError("Password is wrong") from e


def bytes_to_file(path: str | Path, password: str, data: bytes) -> None:
    """Encrypt the `data` with `password` and store base64-encoded result in file at `path`.

    Args:
        path: The path to the result file, in `str` or `pathlib.Path`
        password: The password to encrypt with, in `str`, derived in-function
        data: The data in `bytes` to encrypt

    Returns:
        Nothing.

    Raises:
        ...
    """
    salt = urandom(SALT_SIZE)
    iv = urandom(IV_SIZE)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=KDF_ITERATIONS,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode())

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()

    tag = encryptor.tag
    packed = salt + iv + tag + ciphertext
    b64_data = b64encode(packed)
    Path(path).write_bytes(b64_data)
