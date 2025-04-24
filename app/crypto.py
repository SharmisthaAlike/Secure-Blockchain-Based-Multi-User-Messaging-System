from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

class CryptoHandler:
    def __init__(self):
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey()

    def encrypt_message(self, message, pub_key):
        session_key = get_random_bytes(16)
        cipher_aes = AES.new(session_key, AES.MODE_GCM)
        ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode())
        cipher_rsa = PKCS1_OAEP.new(pub_key)
        enc_session_key = cipher_rsa.encrypt(session_key)
        return enc_session_key + cipher_aes.nonce + tag + ciphertext

    def decrypt_message(self, encrypted_msg):
        enc_session_key = encrypted_msg[:256]
        nonce = encrypted_msg[256:272]
        tag = encrypted_msg[272:288]
        ciphertext = encrypted_msg[288:]
        session_key = PKCS1_OAEP.new(self.private_key).decrypt(enc_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_GCM, nonce)
        return cipher_aes.decrypt_and_verify(ciphertext, tag).decode()
