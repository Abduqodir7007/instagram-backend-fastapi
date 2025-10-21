from sqlalchemy import event
from models import VerifyUser
from datetime import datetime, timedelta
from database import settings

@event.listens_for(VerifyUser, 'before_insert')
def set_expiratio_time(mapper, connection, target):
    target.expiration_time = datetime.utcnow() + timedelta(minutes=settings.OTP_CODE_EXPIRATION_TIME)