from cryptography.fernet import Fernet, InvalidToken
import re
from app.settings import JULEKALENDER_ANSWER_KEY

class Enigma(Fernet):
    def __init__(self, key):
        super().__init__(key)

    def compare_answer(self, txt, ref):
        try:
            ref_decrypt = self.decrypt(ref).decode()
            if isinstance(ref, str):
                ref = bytes(ref, 'UTF-8')

            txt = str(txt).lower().strip()


            if ref_decrypt.startswith("^") and ref_decrypt.endswith("$"):
                pattern = re.compile(ref_decrypt, re.IGNORECASE)
                return pattern.search(txt) is not None

            return str(ref_decrypt).lower() == txt

        except InvalidToken as e:
            return False

        except Exception as e:
            raise Exception(e)

    def encrypt_answer(self, txt):
        return self.encrypt(bytes(txt, 'UTF-8')).decode('UTF-8')

enigma = Enigma(JULEKALENDER_ANSWER_KEY)