from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Guest(Base):
    __tablename__ = "guests"
    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(String, unique=True, index=True, nullable=False)
    total_lifetime_spend = Column(Float, default=0.0)
    average_sentiment = Column(Float, default=0.0)
    stays_count = Column(Integer, default=0)
    last_stay_date = Column(DateTime, nullable=True)
    extra_metadata = Column(JSON, default={})  

    stays = relationship("Stay", back_populates="guest")


class Stay(Base):
    __tablename__ = "stays"
    id = Column(Integer, primary_key=True, index=True)
    stay_id = Column(String, unique=True, index=True, nullable=False)
    guest_id_fk = Column(Integer, ForeignKey("guests.id"))
    check_out_date = Column(DateTime)
    total_spend = Column(Float)
    review_text = Column(Text)
    positive_score = Column(Float, default=0.0)
    negative_score = Column(Float, default=0.0)
    embedding = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    guest = relationship("Guest", back_populates="stays")
