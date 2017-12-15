from Crypto.Cipher import AES
import struct
from hashlib import md5

class CryptoTCP:
    def __init__(self, key = b"0" * 16, iv = b"0" * 16, version = 1):
        self.key = key
        self.iv = iv
        self.version = version

    def Encrypt(self, data=""):
        cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        pack = struct.Struct("h32s")
        pack = pack.pack(self.version, md5(data.encode()).hexdigest().encode())
        pack += cipher.encrypt(data.encode())
        return pack

    def Decrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        unpack = struct.Struct("h32s")
        unpack = unpack.unpack(data[:34])
        version = unpack[0]
        md5 = unpack[1].decode()
        data = cipher.decrypt(data[34:])
        return {
            "version": version,
            "md5": md5,
            "data": data.decode()
        }

if __name__ == "__main__":
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ct = CryptoTCP()
    enc = ct.Encrypt("MDZZ")
    print(enc)
    print(ct.Decrypt(enc))
    s.connect(("127.0.0.1",4999))
    s.sendall(enc)