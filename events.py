from sqlalchemy import event
from models import VerifyUsers
from datetime import datetime, timedelta
from database import settings


@event.listens_for(VerifyUsers, "before_insert")
def set_expiration_time(mapper, connection, target):
    target.expiration_time = datetime.utcnow() + timedelta(
        minutes=settings.OTP_CODE_EXPIRATION_TIME
    )
