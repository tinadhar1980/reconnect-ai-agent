from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CheckoutEvent(BaseModel):
    guest_id: str
    stay_id: str
    check_out_date: datetime
    total_spend: float
    review_text: str

class GuestProfile(BaseModel):
    guest_id: str
    total_lifetime_spend: float
    average_sentiment: float
    stays_count: int
    last_stay_date: Optional[datetime]
    metadata: dict
