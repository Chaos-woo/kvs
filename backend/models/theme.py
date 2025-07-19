from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from . import Base

class Theme(Base):
    """Model for storing theme mode settings"""
    __tablename__ = 'themes'

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String, default='light', nullable=False)  # 'light' or 'dark'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def get_current_theme(cls, db_session):
        """Get the current theme mode, defaults to 'light' if not set"""
        theme = db_session.query(cls).order_by(cls.updated_at.desc()).first()
        return theme.mode if theme else 'light'

    @classmethod
    def set_theme_mode(cls, db_session, mode):
        """Set the theme mode to 'light' or 'dark'"""
        if mode not in ['light', 'dark']:
            raise ValueError("Theme mode must be 'light' or 'dark'")

        # Check if a theme record already exists
        theme = db_session.query(cls).order_by(cls.updated_at.desc()).first()

        if theme:
            # Update existing theme
            theme.mode = mode
        else:
            # Create new theme record
            theme = cls(mode=mode)
            db_session.add(theme)

        db_session.commit()
        return theme
