from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, User


class Speciality(Base):
    __tablename__ = "specialities"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    user: Mapped["User"] = relationship(back_populates="specialities")
    link: Mapped[str] = mapped_column(String(255))
    snils: Mapped[str] = mapped_column(String(255))
    __table_args__ = (
        UniqueConstraint(
            "user_id", "link", name="_duplicates"
        ),
    )
