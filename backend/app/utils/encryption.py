from cryptography.fernet import Fernet, InvalidToken
import re

class Enigma(Fernet):
    def __init__(self, key):
        super().__init__(key)

    def compare_answer(self, txt, ref):
        try:
            if isinstance(ref, str):
                ref = bytes(ref, 'UTF-8')

            txt_lower = str(txt).lower().replace(" ", "")

            ref_decrypt = self.decrypt(ref).decode()
            print(ref_decrypt)

            if ref_decrypt.startswith("^") and ref_decrypt.endswith("$"):
                return re.search(ref_decrypt, txt_lower) is not None

        except InvalidToken as e:
            return False

        return self.decrypt(ref).decode() == txt

    def encrypt_answer(self, txt):
        return self.encrypt(bytes(txt, 'UTF-8')).decode('UTF-8')