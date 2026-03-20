"""
Database models for MAHER AI
SQLAlchemy ORM models for agent storage
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Enum, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import enum
import json
import os

Base = declarative_base()

class AgentStatus(enum.Enum):
    """Agent status enumeration"""
    DRAFT = 'draft'
    PUBLISHED = 'published'

class UserRole(enum.Enum):
    """User role enumeration"""
    GUEST = 'guest'
    ADMIN = 'admin'

class Agent(Base):
    """Agent model for storing user-created and system agents"""
    __tablename__ = 'agents'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Unique identifier for API (e.g., 'agent-1', 'user-agent-abc123')
    agent_id = Column(String(100), unique=True, nullable=False, index=True)

    # Basic information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)

    # Visual customization
    icon_svg = Column(Text, nullable=True)
    icon_background_color = Column(String(20), default='#4f46e5')

    # AI model configuration
    default_provider = Column(String(100), default='MAHER AI Engine')
    display_provider_name = Column(String(100), default='Powered by MAHER AI')

    # Status and metadata
    status = Column(Enum(AgentStatus), default=AgentStatus.DRAFT, nullable=False, index=True)
    is_system = Column(Boolean, default=False, nullable=False, index=True)

    # User tracking (can be expanded for multi-user support)
    created_by = Column(String(100), default='default_user')

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Author Metadata
    network_id = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)

    # ── Skills fields ──────────────────────────────────────────────────────────
    # JSON string: OpenAI function-calling schema  {"type":"function","function":{...}}
    # When present, this agent is a first-class "skill" callable by the OSS model.
    tool_schema = Column(Text, nullable=True)

    # How the skill is implemented
    # llm_agent         → backed by system_prompt + model call  (default)
    # rag_pipeline      → backed by a vector store + model call
    # workflow          → backed by a workflow module
    # local_function    → backed by a Python function in tools/
    implementation_type = Column(String(50), default='llm_agent', nullable=False)

    # Semantic version of the skill interface (bumped when tool_schema changes)
    skill_version = Column(String(20), default='1.0.0', nullable=False)

    def to_dict(self):
        """Convert agent to dictionary for API responses"""
        return {
            'id': self.agent_id,
            'name': self.name,
            'description': self.description,
            'systemPrompt': self.system_prompt,
            'category': self.category,
            'iconSVG': self.icon_svg or self._get_default_icon(),
            'iconBackgroundColor': self.icon_background_color,
            'defaultProvider': self.default_provider,
            'displayProviderName': self.display_provider_name,
            'status': self.status.value if isinstance(self.status, AgentStatus) else self.status,
            'statusText': self._get_status_text(),
            'statusClass': self._get_status_class(),
            'isSystem': self.is_system,
            'createdBy': self.created_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'networkId': self.network_id,
            'department': self.department,
            # Skill fields
            'toolSchema': json.loads(self.tool_schema) if self.tool_schema else None,
            'implementationType': self.implementation_type or 'llm_agent',
            'skillVersion': self.skill_version or '1.0.0',
            'isSkill': bool(self.tool_schema),
        }

    def _get_default_icon(self):
        """Get default icon SVG based on category"""
        icons = {
            'maintenance': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z" /></svg>',
            'operations': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>',
            'safety': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>',
            'other': '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>',
        }
        return icons.get(self.category, icons['other'])

    def _get_status_text(self):
        """Get human-readable status text"""
        if self.is_system:
            return 'Available'
        status_value = self.status.value if isinstance(self.status, AgentStatus) else self.status
        return 'Published' if status_value == 'published' else 'Draft'

    def _get_status_class(self):
        """Get CSS class for status"""
        if self.is_system:
            return 'available'
        status_value = self.status.value if isinstance(self.status, AgentStatus) else self.status
        return 'available' if status_value == 'published' else 'development'


class User(Base):
    """User model for tracking sessions and roles"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), default=UserRole.GUEST, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'session_id': self.session_id,
            'role': self.role.value if isinstance(self.role, UserRole) else self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
        }


class ChatSession(Base):
    """Track chat sessions for analytics"""
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    message_count = Column(Integer, default=1, nullable=False)
    agent_used = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convert chat session to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_count': self.message_count,
            'agent_used': self.agent_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class SiteVisit(Base):
    """Track site visits for analytics"""
    __tablename__ = 'site_visits'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    page = Column(String(200), default='/', nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convert site visit to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'page': self.page,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


# Database setup
DATABASE_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DATABASE_DIR, 'maher_ai.db')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database, create tables, and apply column migrations."""
    Base.metadata.create_all(bind=engine)

    # SQLite does not support ALTER TABLE IF NOT EXISTS — wrap each in try/except
    migrations = [
        "ALTER TABLE agents ADD COLUMN tool_schema TEXT",
        "ALTER TABLE agents ADD COLUMN implementation_type VARCHAR(50) DEFAULT 'llm_agent'",
        "ALTER TABLE agents ADD COLUMN skill_version VARCHAR(20) DEFAULT '1.0.0'",
    ]
    with engine.connect() as conn:
        for ddl in migrations:
            try:
                conn.execute(__import__('sqlalchemy').text(ddl))
                conn.commit()
            except Exception:
                # Column already exists — safe to ignore
                pass

    print(f"Database initialized at: {DATABASE_PATH}")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
