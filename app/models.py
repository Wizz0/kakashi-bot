from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    penalties = Column(Integer, default=0)

    queue_entries = relationship("Queue", back_populates="user")

class Queue(Base):
    __tablename__ = "queue"
    __table_args__ = (
        Index("idx_queue_date", "date"),
        Index("idx_queue_user_id", "user_id")
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_cleaned = Column(Boolean, default=False)

    user = relationship("User", back_populates="queue_entries")

    def __repr__(self):
        return f"Queue(id={self.id}, date={self.date}, user_id={self.user_id}, is_cleaned={self.is_cleaned})"
