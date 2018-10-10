import sys
import argparse
import binascii
import string
from Crypto.Random import random
import pyffx

if __name__=="__main__":
    ap = argparse.ArgumentParser(description="Encrypt a bluetooth command with a given key.")
    ap.add_argument('-k', dest='key', help='The cryptographic key')
    ap.add_argument('-t', dest='text', help='The text to encrypt')
    ap.add_argument('--silent', dest='silent', help='Do only print the result', action='store_true')
    ap.add_argument('--encrypt', help='Encrypt the given text', action="store_true")
    ap.add_argument('--decrypt', help='Decrypt the given text', action="store_true")
    args = ap.parse_args()
    binkey = bytearray(args.key.encode('ascii'))
    if not args.silent:
        print('Key: ' + binascii.hexlify(binkey).decode('ascii'))
    alphabet = 'abcdefghijklmnopqrstuvwxyz1234567890: |'
    cipher = pyffx.String(binkey, alphabet=alphabet, length=50)
    if args.encrypt and not args.decrypt:
        entropy = ''
        for i in range(50 - 1 - len(args.text)):
            entropy += random.choice(alphabet)
        text = args.text.lower() + '|' + entropy
        encrypted = cipher.encrypt(text)
        hexout = binascii.hexlify(encrypted)
        if not args.silent:
            print('Text to encrypt:\n' + text)
            print('Encrypted:\n' + encrypted)
            print('Encrypted text as hex string:\n' + hexout)
            print('Bytes: ' + str(len(hexout) // 2))
        else:
            print(hexout)
    elif args.decrypt:
        input = binascii.unhexlify(args.text).decode(sys.getdefaultencoding())
        decrypted = cipher.decrypt(input)
        decrypted = decrypted[:decrypted.find('|')]
        if not args.silent:
            print('Text to decrypt:\n' + str(input))
            print('Decrypted text:\n' + decrypted)
        else:
            print(decrypted)
    else:
        sys.stderr.write('Error: no action given. Please either add the --encrypt or the --decrypt command.')


