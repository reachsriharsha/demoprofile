"""
User Management Module for handling user login tracking with SQLite database.
Uses SQLAlchemy for database interactions.
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, DateTime, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Create base class for declarative models
Base = declarative_base()

class UserLogin(Base):
    """SQLAlchemy model for user login tracking."""
    __tablename__ = 'user_logins'
    
    email = Column(String(255), primary_key=True)
    last_login_time = Column(DateTime, nullable=False)
    voice_to_text_usage_count = Column(Integer, default=0, nullable=False)
    text_to_voice_usage_count = Column(Integer, default=0, nullable=False)
    pdf_chat_usage_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<UserLogin(email='{self.email}', last_login_time='{self.last_login_time}', voice_to_text_usage_count={self.voice_to_text_usage_count}, text_to_voice_usage_count={self.text_to_voice_usage_count}, pdf_chat_usage_count={self.pdf_chat_usage_count})>"

class UserManager:
    """
    Manages user login tracking using SQLite database with SQLAlchemy.
    """
    
    def __init__(self, db_path: str = "users.db"):
        """
        Initialize the UserManager with database connection.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection and create tables if they don't exist."""
        try:
            # Create engine with SQLite
            self.engine = create_engine(
                f"sqlite:///{self.db_path}",
                echo=False,  # Set to True for SQL query logging
                pool_pre_ping=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            # Run database migrations
            self._run_migrations()
            
            logging.info(f"Database initialized successfully at {self.db_path}")
            
        except SQLAlchemyError as e:
            logging.error(f"Failed to setup database: {e}")
            raise
    
    def _get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def _run_migrations(self):
        """Run database migrations to add new columns if they don't exist."""
        try:
            with self._get_session() as session:
                # Check if pdf_chat_usage_count column exists
                result = session.execute(text("PRAGMA table_info(user_logins)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'pdf_chat_usage_count' not in columns:
                    logging.info("Adding pdf_chat_usage_count column to user_logins table")
                    session.execute(text("ALTER TABLE user_logins ADD COLUMN pdf_chat_usage_count INTEGER DEFAULT 0 NOT NULL"))
                    session.commit()
                    logging.info("Successfully added pdf_chat_usage_count column")
                
        except SQLAlchemyError as e:
            logging.error(f"Failed to run migrations: {e}")
            # Don't raise here, as the database might still be usable
        except Exception as e:
            logging.error(f"Unexpected error during migrations: {e}")
            # Don't raise here, as the database might still be usable
    
    def record_login(self, email: str) -> bool:
        """
        Record or update user login information.
        
        Args:
            email (str): User's email address
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not email or not email.strip():
            logging.warning("Empty email provided for login recording")
            return False
        
        try:
            with self._get_session() as session:
                # Check if user exists
                existing_user = session.query(UserLogin).filter(UserLogin.email == email.strip().lower()).first()
                
                current_time = datetime.now()
                
                if existing_user:
                    # Update existing user's last login time
                    existing_user.last_login_time = current_time
                    logging.info(f"Updated login time for existing user: {email}")
                else:
                    # Create new user record
                    new_user = UserLogin(
                        email=email.strip().lower(),
                        last_login_time=current_time,
                        voice_to_text_usage_count=0,
                        text_to_voice_usage_count=0,
                        pdf_chat_usage_count=0
                    )
                    session.add(new_user)
                    logging.info(f"Created new user record: {email}")
                
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            logging.error(f"Failed to record login for {email}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error recording login for {email}: {e}")
            return False
    
    def get_user_login_info(self, email: str) -> Optional[dict]:
        """
        Get user login information.
        
        Args:
            email (str): User's email address
            
        Returns:
            dict: User login information or None if not found
        """
        if not email or not email.strip():
            return None
        
        try:
            with self._get_session() as session:
                user = session.query(UserLogin).filter(UserLogin.email == email.strip().lower()).first()
                
                if user:
                    return {
                        "email": user.email,
                        "last_login_time": user.last_login_time,
                        "last_login_formatted": user.last_login_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "voice_to_text_usage_count": user.voice_to_text_usage_count,
                        "text_to_voice_usage_count": user.text_to_voice_usage_count,
                        "pdf_chat_usage_count": user.pdf_chat_usage_count
                    }
                return None
                
        except SQLAlchemyError as e:
            logging.error(f"Failed to get user info for {email}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error getting user info for {email}: {e}")
            return None
    
    def get_all_users(self) -> list:
        """
        Get all registered users.
        
        Returns:
            list: List of all user records
        """
        try:
            with self._get_session() as session:
                users = session.query(UserLogin).all()
                return [
                    {
                        "email": user.email,
                        "last_login_time": user.last_login_time,
                        "last_login_formatted": user.last_login_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "voice_to_text_usage_count": user.voice_to_text_usage_count,
                        "text_to_voice_usage_count": user.text_to_voice_usage_count,
                        "pdf_chat_usage_count": user.pdf_chat_usage_count
                    }
                    for user in users
                ]
                
        except SQLAlchemyError as e:
            logging.error(f"Failed to get all users: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error getting all users: {e}")
            return []
    
    def delete_user(self, email: str) -> bool:
        """
        Delete a user record.
        
        Args:
            email (str): User's email address
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not email or not email.strip():
            return False
        
        try:
            with self._get_session() as session:
                user = session.query(UserLogin).filter(UserLogin.email == email.strip().lower()).first()
                
                if user:
                    session.delete(user)
                    session.commit()
                    logging.info(f"Deleted user record: {email}")
                    return True
                else:
                    logging.warning(f"User not found for deletion: {email}")
                    return False
                    
        except SQLAlchemyError as e:
            logging.error(f"Failed to delete user {email}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error deleting user {email}: {e}")
            return False
    
    def get_user_count(self) -> int:
        """
        Get total number of registered users.
        
        Returns:
            int: Number of users
        """
        try:
            with self._get_session() as session:
                count = session.query(UserLogin).count()
                return count
                
        except SQLAlchemyError as e:
            logging.error(f"Failed to get user count: {e}")
            return 0
        except Exception as e:
            logging.error(f"Unexpected error getting user count: {e}")
            return 0
    
    def increment_voice_to_text_usage(self, email: str) -> bool:
        """
        Increment voice-to-text usage count for a user.
        
        Args:
            email (str): User's email address
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not email or not email.strip():
            return False
        
        try:
            with self._get_session() as session:
                user = session.query(UserLogin).filter(UserLogin.email == email.strip().lower()).first()
                
                if user:
                    user.voice_to_text_usage_count += 1
                    session.commit()
                    logging.info(f"Incremented voice-to-text usage for {email}. New count: {user.voice_to_text_usage_count}")
                    return True
                else:
                    logging.warning(f"User not found for voice-to-text usage increment: {email}")
                    return False
                    
        except SQLAlchemyError as e:
            logging.error(f"Failed to increment voice-to-text usage for {email}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error incrementing voice-to-text usage for {email}: {e}")
            return False
    
    def increment_text_to_voice_usage(self, email: str) -> bool:
        """
        Increment text-to-voice usage count for a user.
        
        Args:
            email (str): User's email address
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not email or not email.strip():
            return False
        
        try:
            with self._get_session() as session:
                user = session.query(UserLogin).filter(UserLogin.email == email.strip().lower()).first()
                
                if user:
                    user.text_to_voice_usage_count += 1
                    session.commit()
                    logging.info(f"Incremented text-to-voice usage for {email}. New count: {user.text_to_voice_usage_count}")
                    return True
                else:
                    logging.warning(f"User not found for text-to-voice usage increment: {email}")
                    return False
                    
        except SQLAlchemyError as e:
            logging.error(f"Failed to increment text-to-voice usage for {email}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error incrementing text-to-voice usage for {email}: {e}")
            return False
    
    def increment_pdf_chat_usage(self, email: str) -> bool:
        """
        Increment PDF chat usage count for a user.
        
        Args:
            email (str): User's email address
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not email or not email.strip():
            return False
        
        try:
            with self._get_session() as session:
                user = session.query(UserLogin).filter(UserLogin.email == email.strip().lower()).first()
                
                if user:
                    user.pdf_chat_usage_count += 1
                    session.commit()
                    logging.info(f"Incremented PDF chat usage for {email}. New count: {user.pdf_chat_usage_count}")
                    return True
                else:
                    logging.warning(f"User not found for PDF chat usage increment: {email}")
                    return False
                    
        except SQLAlchemyError as e:
            logging.error(f"Failed to increment PDF chat usage for {email}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error incrementing PDF chat usage for {email}: {e}")
            return False
    
    def check_voice_to_text_quota(self, email: str, max_daily_usage: int = 5) -> dict:
        """
        Check if user has reached their daily voice-to-text quota.
        Resets usage count if more than 24 hours have passed since last login.
        
        Args:
            email (str): User's email address
            max_daily_usage (int): Maximum allowed daily usage (default: 5)
            
        Returns:
            dict: {
                'can_use': bool,
                'current_usage': int,
                'max_usage': int,
                'message': str
            }
        """
        if not email or not email.strip():
            return {
                'can_use': False,
                'current_usage': 0,
                'max_usage': max_daily_usage,
                'message': 'Invalid email provided'
            }
        
        try:
            with self._get_session() as session:
                user = session.query(UserLogin).filter(UserLogin.email == email.strip().lower()).first()
                
                if not user:
                    return {
                        'can_use': False,
                        'current_usage': 0,
                        'max_usage': max_daily_usage,
                        'message': 'User not found'
                    }
                
                current_time = datetime.now()
                time_diff = current_time - user.last_login_time
                hours_since_login = time_diff.total_seconds() / 3600
                
                # If more than 24 hours have passed since last login, reset usage count
                if hours_since_login > 24:
                    user.voice_to_text_usage_count = 0
                    session.commit()
                    logging.info(f"Reset voice-to-text usage count for {email} (last login > 24h ago)")
                
                # Check if user has reached quota
                if user.voice_to_text_usage_count >= max_daily_usage:
                    return {
                        'can_use': False,
                        'current_usage': user.voice_to_text_usage_count,
                        'max_usage': max_daily_usage,
                        'message': f'Your quota of {max_daily_usage} tries reached. Try after 24 hours.'
                    }
                else:
                    return {
                        'can_use': True,
                        'current_usage': user.voice_to_text_usage_count,
                        'max_usage': max_daily_usage,
                        'message': f'Usage: {user.voice_to_text_usage_count}/{max_daily_usage}'
                    }
                    
        except SQLAlchemyError as e:
            logging.error(f"Failed to check voice-to-text quota for {email}: {e}")
            return {
                'can_use': False,
                'current_usage': 0,
                'max_usage': max_daily_usage,
                'message': 'Database error occurred'
            }
        except Exception as e:
            logging.error(f"Unexpected error checking voice-to-text quota for {email}: {e}")
            return {
                'can_use': False,
                'current_usage': 0,
                'max_usage': max_daily_usage,
                'message': 'Unexpected error occurred'
            }
    
    def check_text_to_voice_quota(self, email: str, max_daily_usage: int = 5) -> dict:
        """
        Check if user has reached their daily text-to-voice quota.
        Resets usage count if more than 24 hours have passed since last login.
        
        Args:
            email (str): User's email address
            max_daily_usage (int): Maximum allowed daily usage (default: 5)
            
        Returns:
            dict: {
                'can_use': bool,
                'current_usage': int,
                'max_usage': int,
                'message': str
            }
        """
        if not email or not email.strip():
            return {
                'can_use': False,
                'current_usage': 0,
                'max_usage': max_daily_usage,
                'message': 'Invalid email provided'
            }
        
        try:
            with self._get_session() as session:
                user = session.query(UserLogin).filter(UserLogin.email == email.strip().lower()).first()
                
                if not user:
                    return {
                        'can_use': False,
                        'current_usage': 0,
                        'max_usage': max_daily_usage,
                        'message': 'User not found'
                    }
                
                current_time = datetime.now()
                time_diff = current_time - user.last_login_time
                hours_since_login = time_diff.total_seconds() / 3600
                
                # If more than 24 hours have passed since last login, reset usage count
                if hours_since_login > 24:
                    user.text_to_voice_usage_count = 0
                    session.commit()
                    logging.info(f"Reset text-to-voice usage count for {email} (last login > 24h ago)")
                
                # Check if user has reached quota
                if user.text_to_voice_usage_count >= max_daily_usage:
                    return {
                        'can_use': False,
                        'current_usage': user.text_to_voice_usage_count,
                        'max_usage': max_daily_usage,
                        'message': f'Your quota of {max_daily_usage} tries reached. Try after 24 hours.'
                    }
                else:
                    return {
                        'can_use': True,
                        'current_usage': user.text_to_voice_usage_count,
                        'max_usage': max_daily_usage,
                        'message': f'Usage: {user.text_to_voice_usage_count}/{max_daily_usage}'
                    }
                    
        except SQLAlchemyError as e:
            logging.error(f"Failed to check text-to-voice quota for {email}: {e}")
            return {
                'can_use': False,
                'current_usage': 0,
                'max_usage': max_daily_usage,
                'message': 'Database error occurred'
            }
        except Exception as e:
            logging.error(f"Unexpected error checking text-to-voice quota for {email}: {e}")
            return {
                'can_use': False,
                'current_usage': 0,
                'max_usage': max_daily_usage,
                'message': 'Unexpected error occurred'
            }
    
    def check_pdf_chat_quota(self, email: str, max_daily_usage: int = 5) -> dict:
        """
        Check if user has reached their daily PDF chat quota.
        Resets usage count if more than 24 hours have passed since last login.
        
        Args:
            email (str): User's email address
            max_daily_usage (int): Maximum allowed daily usage (default: 5)
            
        Returns:
            dict: {
                'can_use': bool,
                'current_usage': int,
                'max_usage': int,
                'message': str
            }
        """
        if not email or not email.strip():
            return {
                'can_use': False,
                'current_usage': 0,
                'max_usage': max_daily_usage,
                'message': 'Invalid email provided'
            }
        
        try:
            with self._get_session() as session:
                user = session.query(UserLogin).filter(UserLogin.email == email.strip().lower()).first()
                
                if not user:
                    return {
                        'can_use': False,
                        'current_usage': 0,
                        'max_usage': max_daily_usage,
                        'message': 'User not found'
                    }
                
                current_time = datetime.now()
                time_diff = current_time - user.last_login_time
                hours_since_login = time_diff.total_seconds() / 3600
                
                # If more than 24 hours have passed since last login, reset usage count
                if hours_since_login > 24:
                    user.pdf_chat_usage_count = 0
                    session.commit()
                    logging.info(f"Reset PDF chat usage count for {email} (last login > 24h ago)")
                
                # Check if user has reached quota
                if user.pdf_chat_usage_count >= max_daily_usage:
                    return {
                        'can_use': False,
                        'current_usage': user.pdf_chat_usage_count,
                        'max_usage': max_daily_usage,
                        'message': f'Your quota of {max_daily_usage} PDF chat questions reached. Try after 24 hours.'
                    }
                else:
                    return {
                        'can_use': True,
                        'current_usage': user.pdf_chat_usage_count,
                        'max_usage': max_daily_usage,
                        'message': f'PDF Chat Usage: {user.pdf_chat_usage_count}/{max_daily_usage}'
                    }
                    
        except SQLAlchemyError as e:
            logging.error(f"Failed to check PDF chat quota for {email}: {e}")
            return {
                'can_use': False,
                'current_usage': 0,
                'max_usage': max_daily_usage,
                'message': 'Database error occurred'
            }
        except Exception as e:
            logging.error(f"Unexpected error checking PDF chat quota for {email}: {e}")
            return {
                'can_use': False,
                'current_usage': 0,
                'max_usage': max_daily_usage,
                'message': 'Unexpected error occurred'
            }
    
    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logging.info("Database connections closed")
