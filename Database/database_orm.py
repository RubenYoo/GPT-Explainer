import uuid
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from enum import Enum as PyEnum

Base = declarative_base()


class UploadStatus(PyEnum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    DONE = 'done'
    FAILED = 'failed'


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)

    uploads = relationship('Upload', back_populates='user', cascade='all, delete-orphan')


class Upload(Base):
    __tablename__ = 'upload'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(36), default=str(uuid.uuid4()), nullable=False)
    filename = Column(String(255))
    upload_time = Column(DateTime)
    finish_time = Column(DateTime)
    status = Column(Enum(UploadStatus), default=UploadStatus.PENDING)

    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    user = relationship('User', back_populates='uploads')

    def upload_path(self):
        # TODO
        pass

    def set_finish_time(self):
        # TODO
        pass


if __name__ == '__main__':
    engine = create_engine('sqlite:///db/mydatabase.db', echo=True)
    Base.metadata.create_all(engine)

