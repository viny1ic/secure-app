from Crypto.Cipher import AES
import scrypt, os, binascii

def gettext(filename):
    file = open(filename, "r")
    return eval(file.read())

def settext(filename, Salt, ciphertext, nonce, authTag):
    text = (Salt, ciphertext, nonce, authTag)
    file = open(filename, "w")
    file.write(str(text))

def encrypt(filename, msg, password):
    Salt = os.urandom(16)
    secretKey = scrypt.hash(password.encode("utf-8"), Salt, N=16384, r=8, p=1, buflen=32)
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(msg.encode("utf-8"))
    settext(filename, Salt, ciphertext, aesCipher.nonce, authTag)
    return (Salt, ciphertext, aesCipher.nonce, authTag)

def decrypt(filename, password):
    encryptedMsg = gettext(filename)
    (Salt, ciphertext, nonce, authTag) = encryptedMsg
    secretKey = scrypt.hash(password.encode("utf-8"), Salt, N=16384, r=8, p=1, buflen=32)
    aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
    plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    return plaintext

def fetch(filename):
    return str(gettext(filename)[2])
