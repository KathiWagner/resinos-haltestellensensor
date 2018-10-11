import sys
import argparse
import binascii
import hashlib
import base64
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

def get_raw_signature(file):
    sha512obj = hashlib.sha512()
    with open(file, 'rb') as reader:
        chunk = reader.read(52428800)  # Read 50MB
        while len(chunk) == 52428800:
            sha512obj.update(chunk)
            chunk = reader.read(52428800)  # Read 50MB
        if len(chunk) > 0:
            sha512obj.update(chunk)
    if sha512obj.digest_size > 0:
        return sha512obj.hexdigest()
    else:
        raise AssertionError('Sha512 digest size for input file is 0')

def sign(key, file, signaturefile):
        raw_signature = get_raw_signature(file)
        cipher = AESCipher(key)
        signature = cipher.encrypt(raw_signature)
        with open(signaturefile, 'w') as writer:
            writer.write(signature)

def check(key, file, signaturefile):
    raw_signature = get_raw_signature(file)
    cipher = AESCipher(key)
    with open(signaturefile, 'r') as reader:
        foreign_sig = reader.read().rstrip()
        if cipher.decrypt(foreign_sig) == raw_signature:
            return True
    return False

if __name__=="__main__":
    ap = argparse.ArgumentParser(description="Create or check file signature (sha512 with AES in ECB mode)")
    ap.add_argument('-k', dest='key', help='The cryptographic key')
    ap.add_argument('-f', dest='file', help='The signed file')
    ap.add_argument('-s', dest='sig_file', help='The signature file')
    ap.add_argument('--silent', dest='silent', help='Do only print the result', action='store_true')
    ap.add_argument('--sign', help='Sign the given file', action="store_true")
    ap.add_argument('--check', help='Check the ', action="store_true")
    args = ap.parse_args()
    #binkey = bytearray(args.key.encode('ascii'))
    #if not args.silent:
    #    print('Key: ' + binascii.hexlify(binkey).decode('ascii'))
    if args.check and not args.sign:
        if check(args.key, args.file, args.sig_file):
            print('Match')
            sys.exit(0)
        else:
            print('No match')
            sys.exit(1)

    elif args.sign:
        sign(args.key, args.file, args.sig_file)
        if not args.silent:
            print('Successfully created signature in file ' + args.sig_file)
        sys.exit(0)


