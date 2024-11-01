from argon2 import PasswordHasher


class PasswordManager:
    ph = PasswordHasher()

    def hash_password(self, password):
        return self.ph.hash(password)

    def verify_password(self, hashed_password, current_password):
        return self.ph.verify(hashed_password, current_password)
