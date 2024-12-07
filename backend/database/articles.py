from sqlalchemy import Column, String, DateTime, Computed, Text, func

from backend.database import Base


class ArticleModel(Base):
    __tablename__ = "articles"

    filename = Column(String, primary_key=True)
    sourcepdf_url = Column(Text)
    processeds3_url = Column(Text)
    a_id = Column("a_id", String, primary_key=True, nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = {"schema": "public"}
