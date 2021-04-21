from sqlalchemy import Table, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from .messages import Message
from .users import User


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    friend_id = Column(Integer, ForeignKey(User.id, ondelete='SET NULL'), nullable=False)
    name = Column(String, nullable=False)

    owner = relationship(User, foreign_keys=[owner_id], backref='contacts')
    friend = relationship(User, foreign_keys=[friend_id])
    messages = relationship(Message, secondary=lambda: contact_messages_table)


contact_messages_table = Table(
    'contact_messages', Base.metadata,
    Column('contact_id', Integer, ForeignKey(Contact.id, ondelete='CASCADE'), primary_key=True),
    Column('message_id', Integer, ForeignKey(Message.id, ondelete='CASCADE'), primary_key=True),
)
