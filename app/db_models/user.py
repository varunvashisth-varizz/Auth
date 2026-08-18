from datetime import datetime, timezone

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..db.database import base


# NOTE: this file/table did not exist in the original repository even
# though `app/services/authenticate_service.py` already did
# `from ..db_models.user import user`. This model is new and simply
# fulfills that pre-existing import so the JWT flow can actually run
# against a real table. The class name `user` matches the name that
# was already being imported elsewhere, so no call sites change.
class user(base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
