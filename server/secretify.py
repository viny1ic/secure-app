from Crypto.Cipher import AES
import scrypt, os, binascii

def gettext(filename):
    """
    Reads text from file and returns the evaluated data structure
    """
    file = open(filename, "r")
    return eval(file.read())

def settext(filename, Salt, ciphertext, nonce, authTag):
    """
    Stores the given ciphertext with the salt, nonce and authtag
    """
    text = (Salt, ciphertext, nonce, authTag)
    file = open(filename, "w")
    file.write(str(text))

def encrypt(filename, msg, password):
    """
    Encrypts the supplied message using the password as a key using PBKDF
    """
    Salt = os.urandom(16)
    secretKey = scrypt.hash(password.encode("utf-8"), Salt, N=16384, r=8, p=1, buflen=32)
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(msg.encode("utf-8"))
    settext(filename, Salt, ciphertext, aesCipher.nonce, authTag)
    return (Salt, ciphertext, aesCipher.nonce, authTag)

def decrypt(filename, password):
    """
    Decrypts the content of the supplied filename using the password provided
    """
    encryptedMsg = gettext(filename)
    (Salt, ciphertext, nonce, authTag) = encryptedMsg
    try:
        secretKey = scrypt.hash(password.encode("utf-8"), Salt, N=16384, r=8, p=1, buflen=32)
        aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
        plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    except Exception as e:
        print(e)
        return "Failed to decrypt the cipher. Please check the supplied values".encode("utf-8")
    return plaintext

def fetch(filename):
    """
    Returns ciphertext associated with the supplied filename
    """
    return str(gettext(filename)[2])
