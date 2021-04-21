from sqlalchemy import Boolean, Column, Integer, String, LargeBinary
import bcrypt
from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_banned = Column(Boolean, default=False)
    avatar = Column(LargeBinary)

    @classmethod
    def generate_password_hash(cls, password: str) -> str:
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return password_hash.decode()

    def set_password(self, value: str) -> None:
        self.password_hash = self.generate_password_hash(value)

    def check_password(self, value: str) -> bool:
        password = value.encode()
        password_hash = self.password_hash.encode()
        return bcrypt.checkpw(password, password_hash)
