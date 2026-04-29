import os
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def derive_chunk_key(master_key: bytes, file_id: str, chunk_index: int) -> bytes:
    """Derives a secure, unique 32-byte key for each chunk."""
    message = f"{file_id}:{chunk_index}".encode()
    return hmac.new(master_key, message, hashlib.sha256).digest()

def encrypt_chunk(data: bytes, key: bytes) -> bytes:
    """Encrypts chunk data using AES-GCM and prepends the nonce."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12) # AES-GCM requires a 12-byte nonce
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def decrypt_chunk(encrypted_data: bytes, key: bytes) -> bytes:
    """Extracts the nonce and decrypts the chunk data."""
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

def checksum(data: bytes, chunk_size=1048576): # 1MB
    '''calculate this to check the duplicacy of a file'''
    h = hashlib.sha1()
    while chunk := data.read(chunk_size): 
        h.update(chunk)
    return h.hexdigest()