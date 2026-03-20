"""
MAHER AI - Flask Backend API
Production-ready Flask server with unified model provider support
Supports MetaBrain (primary) and Gemini (fallback)
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
import os
import logging
from dotenv import load_dotenv
import requests
from typing import Dict, Any, List
import json
import uuid
import tempfile
from datetime import datetime, timedelta

# Import file parser for agent knowledge
from file_parser import FileParser

# Import database models
from models import Agent, AgentStatus, SessionLocal, init_db, User, UserRole, ChatSession, SiteVisit

# Import unified model client
from model_client import get_model_client, MAHERModelClient

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logger.info(f"Loaded configuration from {dotenv_path}")
else:
    # Fallback to local .env if config folder differs
    load_dotenv()
    logger.warning("Config .env not found in ../../config/.env, using default behavior")

# Initialize Flask app
app = Flask(__name__, static_folder='../dist', static_url_path='')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max request size (for file uploads)

# Knowledge storage directory
KNOWLEDGE_STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'knowledge_storage')
os.makedirs(KNOWLEDGE_STORAGE_DIR, exist_ok=True)

# CORS configuration - Update with your production domain
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Session-ID"],
        "expose_headers": ["X-Session-ID"],
        "max_age": 3600
    }
})

# Rate limiting - Adjust based on your needs
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get('REDIS_URL', 'memory://')
)

# Initialize unified model client
# Providers (in priority order based on MODEL_PROVIDER env var):
#   gpt-oss   → self-hosted vLLM (Qwen 3 / GPT-OSS)  [set VLLM_SERVER_URL]
#   metabrain → Aramco enterprise AI                  [set METABRAIN_CLIENT_ID/SECRET]
#   gemini    → Google Gemini                         [set GEMINI_API_KEY]
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
model_client: MAHERModelClient = get_model_client(
    gemini_api_key=GEMINI_API_KEY,
    vllm_server_url=os.environ.get('VLLM_SERVER_URL', ''),
    vllm_model_path=os.environ.get('VLLM_MODEL_PATH', '/home/cdsw/gpt-oss'),
)

# Skills Orchestrator — initialised lazily to avoid startup failure if
# registry.json is temporarily absent during first deploy.
_skills_orchestrator = None

def get_skills_orchestrator():
    """Return (creating once) the SkillsOrchestrator singleton."""
    global _skills_orchestrator
    if _skills_orchestrator is None:
        registry_path = os.path.join(os.path.dirname(__file__), 'registry.json')
        try:
            from skills_orchestrator import SkillsOrchestrator
            _skills_orchestrator = SkillsOrchestrator(
                model_client=model_client,
                registry_path=registry_path,
            )
            logger.info("SkillsOrchestrator initialised")
        except Exception as exc:
            logger.error(f"SkillsOrchestrator init failed: {exc}")
    return _skills_orchestrator

# Admin password configuration
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'maher_admin_2026')

if not model_client.get_active_provider() or model_client.get_active_provider() == "none":
    logger.warning(
        "WARNING: No AI model provider configured! "
        "Set METABRAIN_CLIENT_ID/SECRET or GEMINI_API_KEY in .env. "
        "AI features will be unavailable."
    )
else:
    logger.info(f"Active AI provider: {model_client.get_active_provider()}")

# Initialize database on startup
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")


# ============================================================================
# Agent Knowledge Storage Helper Functions
# ============================================================================

def get_agent_knowledge_path(agent_id: str) -> str:
    """Get the storage path for an agent's knowledge"""
    return os.path.join(KNOWLEDGE_STORAGE_DIR, f"{agent_id}.json")


def load_agent_knowledge(agent_id: str) -> Dict:
    """Load agent knowledge from storage"""
    path = get_agent_knowledge_path(agent_id)
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading agent knowledge: {str(e)}")
    return {'agent_id': agent_id, 'documents': [], 'created_at': datetime.now().isoformat()}


def save_agent_knowledge(agent_id: str, knowledge: Dict) -> None:
    """Save agent knowledge to storage"""
    path = get_agent_knowledge_path(agent_id)
    try:
        knowledge['updated_at'] = datetime.now().isoformat()
        with open(path, 'w') as f:
            json.dump(knowledge, f, indent=2)
        logger.info(f"Saved knowledge for agent: {agent_id}")
    except Exception as e:
        logger.error(f"Error saving agent knowledge: {str(e)}")
        raise


def delete_agent_knowledge(agent_id: str) -> bool:
    """Delete agent knowledge from storage"""
    path = get_agent_knowledge_path(agent_id)
    if os.path.exists(path):
        try:
            os.remove(path)
            logger.info(f"Deleted knowledge for agent: {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting agent knowledge: {str(e)}")
            raise
    return False


@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (JS, CSS, images)"""
    try:
        return send_from_directory(app.static_folder, path)
    except Exception:
        # If file not found, serve index.html (for React Router)
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with model provider status"""
    return jsonify({
        'status': 'healthy',
        'service': 'MAHER AI Backend',
        'version': '2.0.0',
        'model_providers': model_client.get_status()
    }), 200


# ============================================================================
# Authentication Endpoints
# ============================================================================

def is_admin(session_id: str) -> bool:
    """Helper function to check if session is admin"""
    if not session_id:
        return False
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(session_id=session_id).first()
        return user and user.role == UserRole.ADMIN
    finally:
        db.close()


@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def admin_login():
    """
    Admin login endpoint
    
    Request: {"password": "admin_password"}
    Response: {"success": true, "role": "admin", "session_id": "..."}
    """
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if password == ADMIN_PASSWORD:
            # Create admin session
            session_id = str(uuid.uuid4())
            
            # Store in database
            db = SessionLocal()
            try:
                user = User(session_id=session_id, role=UserRole.ADMIN)
                db.add(user)
                db.commit()
                
                logger.info(f"Admin login successful: {session_id[:8]}...")
                
                return jsonify({
                    'success': True,
                    'role': 'admin',
                    'session_id': session_id
                }), 200
            finally:
                db.close()
        else:
            logger.warning("Failed admin login attempt")
            return jsonify({'success': False, 'error': 'Invalid password'}), 401
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/auth/session', methods=['POST'])
def create_guest_session():
    """
    Create or retrieve guest session
    
    Request: {"session_id": "optional_existing_id"}
    Response: {"session_id": "...", "role": "guest"}
    """
    try:
        data = request.get_json() or {}
        existing_session = data.get('session_id')
        
        db = SessionLocal()
        try:
            if existing_session:
                # Check if session exists
                user = db.query(User).filter_by(session_id=existing_session).first()
                if user:
                    user.last_active = datetime.utcnow()
                    db.commit()
                    return jsonify({
                        'session_id': user.session_id,
                        'role': user.role.value
                    }), 200
            
            # Create new guest session
            session_id = str(uuid.uuid4())
            user = User(session_id=session_id, role=UserRole.GUEST)
            db.add(user)
            db.commit()
            
            logger.info(f"Guest session created: {session_id[:8]}...")
            
            return jsonify({
                'session_id': session_id,
                'role': 'guest'
            }), 200
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Session creation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/auth/verify', methods=['POST'])
def verify_session():
    """
    Verify session and return role
    
    Request: {"session_id": "..."}
    Response: {"valid": true, "role": "guest|admin"}
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'valid': False}), 400
        
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(session_id=session_id).first()
            if user:
                # Update last active
                user.last_active = datetime.utcnow()
                db.commit()
                
                return jsonify({
                    'valid': True,
                    'role': user.role.value
                }), 200
            else:
                return jsonify({'valid': False}), 404
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Session verification error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    Logout (delete session)
    
    Request: {"session_id": "..."}
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False}), 400
        
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(session_id=session_id).first()
            if user:
                db.delete(user)
                db.commit()
                logger.info(f"User logged out: {session_id[:8]}...")
            return jsonify({'success': True}), 200
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Analytics Endpoints (Admin Only)
# ============================================================================

@app.route('/api/admin/analytics', methods=['GET'])
@limiter.limit("30 per minute")
def get_analytics():
    """
    Get analytics dashboard data (admin only)
    
    Headers: {"X-Session-ID": "admin_session_id"}
    
    Returns:
        {
            "total_visits": 1234,
            "total_chats": 567,
            "total_agents": 15,
            "active_users": 23,
            "visits_today": 45,
            "chats_today": 89,
            "top_agents": [...],
            "recent_activity": [...]
        }
    """
    try:
        session_id = request.headers.get('X-Session-ID')
        
        # Verify admin
        if not is_admin(session_id):
            return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
        
        db = SessionLocal()
        try:
            from sqlalchemy import func
            
            today = datetime.utcnow().date()
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            # Total visits
            total_visits = db.query(func.count(SiteVisit.id)).scalar() or 0
            
            # Total chats
            total_chats = db.query(func.count(ChatSession.id)).scalar() or 0
            
            # Total agents
            total_agents = db.query(func.count(Agent.id)).scalar() or 0
            
            # Active users (last 24 hours)
            active_users = db.query(func.count(func.distinct(User.session_id)))\
                .filter(User.last_active >= yesterday).scalar() or 0
            
            # Visits today
            visits_today = db.query(func.count(SiteVisit.id))\
                .filter(func.date(SiteVisit.timestamp) == today).scalar() or 0
            
            # Chats today
            chats_today = db.query(func.count(ChatSession.id))\
                .filter(func.date(ChatSession.created_at) == today).scalar() or 0
            
            # Top agents (by usage)
            top_agents_query = db.query(
                ChatSession.agent_used,
                func.count(ChatSession.id).label('usage_count')
            ).filter(ChatSession.agent_used.isnot(None))\
             .group_by(ChatSession.agent_used)\
             .order_by(func.count(ChatSession.id).desc())\
             .limit(5).all()
            
            top_agents = [
                {'agent': agent, 'count': count}
                for agent, count in top_agents_query
            ]
            
            # Recent activity
            recent_sessions = db.query(ChatSession)\
                .order_by(ChatSession.created_at.desc())\
                .limit(10).all()
            
            recent_activity = [
                {
                    'id': session.id,
                    'agent': session.agent_used or 'Unknown',
                    'messages': session.message_count,
                    'time': session.created_at.isoformat() if session.created_at else None
                }
                for session in recent_sessions
            ]
            
            logger.info(f"Analytics requested by admin: {session_id[:8]}...")
            
            return jsonify({
                'total_visits': total_visits,
                'total_chats': total_chats,
                'total_agents': total_agents,
                'active_users': active_users,
                'visits_today': visits_today,
                'chats_today': chats_today,
                'top_agents': top_agents,
                'recent_activity': recent_activity
            }), 200
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Agent Management Endpoints
# ============================================================================

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """
    Get all published agents (system + user-created)
    Query params:
        - status: filter by status (draft, published)
        - category: filter by category
        - user: get specific user's agents (default: default_user)
    """
    try:
        db = SessionLocal()


        # Get query parameters
        status = request.args.get('status')
        category = request.args.get('category')
        user = request.args.get('user', 'default_user')
        include_drafts = request.args.get('include_drafts', 'false').lower() == 'true'
        view_mode = request.args.get('view_mode', 'personal') # 'personal' or 'all' (admin only)

        # Check admin for 'all' view mode
        session_id = request.headers.get('X-Session-ID')
        is_admin_user = is_admin(session_id)
        
        if view_mode == 'all' and not is_admin_user:
            return jsonify({'error': 'Unauthorized. Admin access required for full view.'}), 403

        # Build query
        query = db.query(Agent)

        # Filter by status
        if include_drafts:
            if view_mode == 'all' and is_admin_user:
                 # Admin sees ALL agents (drafts and published) from everyone
                 pass
            else:
                # User sees their own agents (drafts + published) + all system agents
                query = query.filter(
                    ((Agent.created_by == user) | (Agent.is_system == True))
                )
        else:
            # Only published agents (default for Toolroom)
            query = query.filter(Agent.status == AgentStatus.PUBLISHED)

        # Filter by category if specified
        if category:
            query = query.filter(Agent.category == category)

        # Execute query
        agents = query.order_by(Agent.is_system.desc(), Agent.created_at.desc()).all()

        # Convert to dict
        agents_data = [agent.to_dict() for agent in agents]

        db.close()

        return jsonify({
            'success': True,
            'agents': agents_data,
            'count': len(agents_data)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching agents: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch agents'
        }), 500


@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id: str):
    """Get a single agent by ID"""
    try:
        db = SessionLocal()
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        db.close()

        if not agent:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404

        return jsonify({
            'success': True,
            'agent': agent.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Error fetching agent {agent_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch agent'
        }), 500


@app.route('/api/agents', methods=['POST'])
@limiter.limit("50 per hour")
def create_agent():
    """
    Create a new agent (saved as draft by default)
    Request body:
        - name: Agent name
        - description: Agent description
        - systemPrompt: System prompt/instructions
        - category: Agent category
        - iconSVG: (optional) Custom icon SVG
        - iconBackgroundColor: (optional) Icon background color
        - defaultProvider: (optional) AI model provider
        - status: (optional) 'draft' or 'published' (default: draft)
    """
    try:
        # Authorization check:
        # - Guests CAN create agents (as drafts only)
        # - Admins CAN create agents (draft or published)
        
        session_id = request.headers.get('X-Session-ID')
        is_admin_user = is_admin(session_id)
        
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Enforce Draft status for non-admins
        requested_status = data.get('status', 'draft')
        if not is_admin_user and requested_status != 'draft':
            return jsonify({'error': 'Guests can only create draft agents.'}), 403
            
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['name', 'description', 'systemPrompt', 'category']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        db = SessionLocal()

        # Generate unique agent ID
        agent_id = f"user-agent-{uuid.uuid4().hex[:12]}"

        # Create new agent
        agent = Agent(
            agent_id=agent_id,
            name=data['name'],
            description=data['description'],
            system_prompt=data['systemPrompt'],
            category=data['category'],
            icon_svg=data.get('iconSVG'),
            icon_background_color=data.get('iconBackgroundColor', '#4f46e5'),
            default_provider=data.get('defaultProvider', 'MAHER AI Engine'),
            display_provider_name=data.get('displayProviderName', 'Powered by MAHER AI'),
            status=AgentStatus.DRAFT if data.get('status', 'draft') == 'draft' else AgentStatus.PUBLISHED,
            is_system=False,
            created_by=data.get('createdBy', 'default_user'),
            network_id=data.get('networkId'),
            department=data.get('department')
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)

        agent_dict = agent.to_dict()
        db.close()

        logger.info(f"Created new agent: {agent.name} (ID: {agent.agent_id})")

        return jsonify({
            'success': True,
            'message': 'Agent created successfully',
            'agent': agent_dict
        }), 201

    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create agent'
        }), 500


@app.route('/api/agents/<agent_id>', methods=['PUT'])
@limiter.limit("50 per hour")
def update_agent(agent_id: str):
    """Update an existing agent (admin only)"""
    try:
        # Check admin authorization
        session_id = request.headers.get('X-Session-ID')
        if not is_admin(session_id):
            return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
        
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        db = SessionLocal()
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()

        if not agent:
            db.close()
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404

        # Don't allow updating system agents
        if agent.is_system:
            db.close()
            return jsonify({
                'success': False,
                'error': 'Cannot update system agents'
            }), 403

        # Update fields if provided
        if 'name' in data:
            agent.name = data['name']
        if 'description' in data:
            agent.description = data['description']
        if 'systemPrompt' in data:
            agent.system_prompt = data['systemPrompt']
        if 'category' in data:
            agent.category = data['category']
        if 'iconSVG' in data:
            agent.icon_svg = data['iconSVG']
        if 'iconBackgroundColor' in data:
            agent.icon_background_color = data['iconBackgroundColor']
        if 'defaultProvider' in data:
            agent.default_provider = data['defaultProvider']
        if 'displayProviderName' in data:
            agent.display_provider_name = data['displayProviderName']
        if 'networkId' in data:
            agent.network_id = data['networkId']
        if 'department' in data:
            agent.department = data['department']
        if 'status' in data:
            # Convert string to enum
            status_value = data['status']
            if status_value == 'draft':
                agent.status = AgentStatus.DRAFT
            elif status_value == 'published':
                agent.status = AgentStatus.PUBLISHED

        agent.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(agent)

        agent_dict = agent.to_dict()
        db.close()

        logger.info(f"Updated agent: {agent.name} (ID: {agent.agent_id})")

        return jsonify({
            'success': True,
            'message': 'Agent updated successfully',
            'agent': agent_dict
        }), 200

    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update agent'
        }), 500


@app.route('/api/agents/<agent_id>/publish', methods=['PUT'])
@limiter.limit("50 per hour")
def publish_agent(agent_id: str):
    """Publish an agent (change status from draft to published)"""
    try:
        db = SessionLocal()
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()

        if not agent:
            db.close()
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404

        # Don't allow publishing system agents (they're already published)
        if agent.is_system:
            db.close()
            return jsonify({
                'success': False,
                'error': 'System agents are already published'
            }), 403

        # Update status to published
        agent.status = AgentStatus.PUBLISHED
        agent.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(agent)

        agent_dict = agent.to_dict()
        db.close()

        logger.info(f"Published agent: {agent.name} (ID: {agent.agent_id})")

        return jsonify({
            'success': True,
            'message': 'Agent published successfully',
            'agent': agent_dict
        }), 200

    except Exception as e:
        logger.error(f"Error publishing agent {agent_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to publish agent'
        }), 500


@app.route('/api/agents/<agent_id>', methods=['DELETE'])
@limiter.limit("50 per hour")
def delete_agent(agent_id: str):
    """Delete an agent (admin only)"""
    try:
        # Check admin authorization
        session_id = request.headers.get('X-Session-ID')
        if not is_admin(session_id):
            return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
        
        db = SessionLocal()
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()

        if not agent:
            db.close()
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404

        # Don't allow deleting system agents
        if agent.is_system:
            db.close()
            return jsonify({
                'success': False,
                'error': 'Cannot delete system agents'
            }), 403

        agent_name = agent.name
        db.delete(agent)
        db.commit()
        db.close()

        logger.info(f"Deleted agent: {agent_name} (ID: {agent_id})")

        return jsonify({
            'success': True,
            'message': 'Agent deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete agent'
        }), 500






# ============================================================================
# Agent Knowledge Management Endpoints
# ============================================================================

@app.route('/api/knowledge/upload', methods=['POST'])
@limiter.limit("20 per hour")
def upload_knowledge():
    """
    Upload files as agent knowledge

    Form data:
        - agent_id: ID of the agent
        - files: Multiple files (PDF, TXT, DOCX)
    """
    try:
        # Check if agent_id is provided
        agent_id = request.form.get('agent_id')
        if not agent_id:
            return jsonify({'error': 'agent_id is required'}), 400

        # Check if files are provided
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({'error': 'No files provided'}), 400

        # Limit number of files
        MAX_FILES = 5
        if len(files) > MAX_FILES:
            return jsonify({'error': f'Maximum {MAX_FILES} files allowed'}), 400

        # Load existing knowledge
        knowledge = load_agent_knowledge(agent_id)

        # Check total files limit
        existing_count = len(knowledge.get('documents', []))
        if existing_count + len(files) > MAX_FILES:
            return jsonify({
                'error': f'Maximum {MAX_FILES} files allowed per agent. Currently have {existing_count} files.'
            }), 400

        # Process each file
        processed_files = []
        errors = []

        for file in files:
            try:
                # Parse file
                parsed_data = FileParser.parse_file(file)

                # Add metadata
                file_id = str(uuid.uuid4())
                parsed_data['id'] = file_id
                parsed_data['uploaded_at'] = datetime.now().isoformat()

                # Add to knowledge base
                knowledge['documents'].append(parsed_data)
                processed_files.append({
                    'id': file_id,
                    'filename': parsed_data['filename'],
                    'size': parsed_data['size'],
                    'word_count': parsed_data['word_count']
                })

                logger.info(f"Processed file: {parsed_data['filename']} for agent: {agent_id}")

            except Exception as e:
                error_msg = f"Error processing {file.filename}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Save updated knowledge
        if processed_files:
            save_agent_knowledge(agent_id, knowledge)

        response = {
            'success': True,
            'agent_id': agent_id,
            'processed_files': processed_files,
            'total_files': len(knowledge['documents'])
        }

        if errors:
            response['errors'] = errors
            response['partial_success'] = True

        return jsonify(response), 200 if not errors else 207

    except Exception as e:
        logger.error(f"Error in upload_knowledge: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@app.route('/api/knowledge/agents/<agent_id>', methods=['GET'])
@limiter.limit("100 per hour")
def get_agent_knowledge(agent_id: str):
    """Get agent's knowledge base"""
    try:
        knowledge = load_agent_knowledge(agent_id)
        summary = FileParser.get_knowledge_summary(knowledge.get('documents', []))

        return jsonify({
            'agent_id': agent_id,
            'knowledge': knowledge,
            'summary': summary
        }), 200

    except Exception as e:
        logger.error(f"Error getting agent knowledge: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/knowledge/agents/<agent_id>', methods=['DELETE'])
@limiter.limit("20 per hour")
def delete_agent_knowledge_endpoint(agent_id: str):
    """Delete all knowledge for an agent"""
    try:
        deleted = delete_agent_knowledge(agent_id)

        if deleted:
            return jsonify({
                'success': True,
                'message': f'Deleted all knowledge for agent {agent_id}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No knowledge found for this agent'
            }), 404

    except Exception as e:
        logger.error(f"Error deleting agent knowledge: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/knowledge/agents/<agent_id>/files/<file_id>', methods=['DELETE'])
@limiter.limit("50 per hour")
def delete_knowledge_file(agent_id: str, file_id: str):
    """Delete a specific file from agent's knowledge"""
    try:
        knowledge = load_agent_knowledge(agent_id)

        # Find and remove the file
        documents = knowledge.get('documents', [])
        initial_count = len(documents)

        knowledge['documents'] = [doc for doc in documents if doc.get('id') != file_id]

        if len(knowledge['documents']) == initial_count:
            return jsonify({
                'success': False,
                'message': 'File not found'
            }), 404

        # Save updated knowledge
        save_agent_knowledge(agent_id, knowledge)

        return jsonify({
            'success': True,
            'message': 'File deleted successfully',
            'remaining_files': len(knowledge['documents'])
        }), 200

    except Exception as e:
        logger.error(f"Error deleting knowledge file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/chat/generate', methods=['POST'])
@limiter.limit("60 per minute")
def generate_chat():
    """
    Chat generation endpoint using unified model client.
    Routes through MetaBrain (primary) or Gemini (fallback).
    Supports agent knowledge context.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        contents = data.get('contents', [])
        system_instruction = data.get('systemInstruction')
        generation_config = data.get('generationConfig', {})
        agent_id = data.get('agentId')  # Optional: for knowledge context

        if not contents:
            return jsonify({'error': 'Contents are required'}), 400

        # If agent_id provided, load and include knowledge context
        if agent_id:
            try:
                knowledge = load_agent_knowledge(agent_id)
                documents = knowledge.get('documents', [])

                if documents:
                    knowledge_context = FileParser.create_knowledge_context(documents)
                    if system_instruction:
                        system_instruction = f"{knowledge_context}\n\n{system_instruction}"
                    else:
                        system_instruction = knowledge_context
                    logger.info(f"Added {len(documents)} documents as context for agent {agent_id}")
            except Exception as e:
                logger.warning(f"Could not load knowledge for agent {agent_id}: {str(e)}")

        # Extract user prompt from contents (last user message)
        prompt = ""
        for msg in reversed(contents):
            if msg.get("role") == "user":
                parts = msg.get("parts", [])
                prompt = " ".join(p.get("text", "") for p in parts if "text" in p)
                break

        if not prompt:
            return jsonify({'error': 'No user message found in contents'}), 400

        active_provider = model_client.get_active_provider()
        logger.info(f"Chat generate using provider: {active_provider}")

        # Generate response through unified client
        result = model_client.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            contents=contents,
            generation_config=generation_config,
            temperature=generation_config.get('temperature', 0.7),
        )

        if not result.success:
            return jsonify({
                'error': f'AI service error: {result.error}',
                'provider': result.provider,
            }), 503

        # Return in Gemini-compatible format for frontend compatibility
        return jsonify(result.to_gemini_format()), 200

    except Exception as e:
        logger.error(f"Unexpected error in generate_chat: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/chat/stream', methods=['POST'])
@limiter.limit("20 per minute")
def stream_chat():
    """
    Streaming chat endpoint.
    Uses Gemini streaming when available, falls back to non-streaming
    MetaBrain response wrapped as a single chunk.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        contents = data.get('contents', [])
        system_instruction = data.get('systemInstruction')
        generation_config = data.get('generationConfig', {})

        if not contents:
            return jsonify({'error': 'Contents are required'}), 400

        active_provider = model_client.get_active_provider()
        logger.info(f"Stream chat using provider: {active_provider}")

        if active_provider == "gemini" and model_client.gemini.is_available():
            # Gemini supports native streaming
            payload = {'contents': contents}
            if system_instruction:
                payload['systemInstruction'] = {'parts': [{'text': system_instruction}]}
            if generation_config:
                payload['generationConfig'] = generation_config

            def generate():
                response = model_client.gemini.stream_raw(payload)
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk

            return app.response_class(
                generate(),
                mimetype='application/json',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )
        else:
            # MetaBrain doesn't support streaming - return full response as single chunk
            prompt = ""
            for msg in reversed(contents):
                if msg.get("role") == "user":
                    parts = msg.get("parts", [])
                    prompt = " ".join(p.get("text", "") for p in parts if "text" in p)
                    break

            result = model_client.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                contents=contents,
                generation_config=generation_config,
            )

            # Wrap as streaming-compatible response
            response_json = json.dumps(result.to_gemini_format())

            def single_chunk():
                yield response_json.encode('utf-8')

            return app.response_class(
                single_chunk(),
                mimetype='application/json',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )

    except Exception as e:
        logger.error(f"Unexpected error in stream_chat: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/files/extract', methods=['POST'])
@limiter.limit("30 per minute")
def extract_file_content():
    """
    Extract text content from uploaded files (PDF, Word, Excel)
    Max file size: 2 MB per file
    """
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files provided'}), 400

        max_size = 2 * 1024 * 1024  # 2 MB
        allowed_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx'}

        extracted_files = []
        errors = []

        for file in files:
            if file.filename == '':
                continue

            # Get file extension
            filename = secure_filename(file.filename)
            _, ext = os.path.splitext(filename.lower())

            # Validate file type
            if ext not in allowed_extensions:
                errors.append(f'{filename}: Unsupported file type. Only PDF, Word, and Excel files are allowed.')
                continue

            # Read file content to check size
            file_content = file.read()
            if len(file_content) > max_size:
                errors.append(f'{filename}: File size exceeds 2 MB limit ({len(file_content) / (1024 * 1024):.2f} MB)')
                continue

            # Save temporarily and extract content
            temp_dir = os.path.join(os.path.dirname(__file__), 'temp_uploads')
            os.makedirs(temp_dir, exist_ok=True)

            temp_path = os.path.join(temp_dir, filename)
            try:
                with open(temp_path, 'wb') as f:
                    f.write(file_content)

                # Extract text content using FileParser
                try:
                    if ext == '.pdf':
                        content = FileParser.extract_text_from_pdf(temp_path)
                    elif ext in ['.doc', '.docx']:
                        content = FileParser.extract_text_from_word(temp_path)
                    elif ext in ['.xls', '.xlsx']:
                        content = FileParser.extract_text_from_excel(temp_path)
                    else:
                        content = ""

                    # Limit content length (max 50,000 characters to avoid token limits)
                    if len(content) > 50000:
                        content = content[:50000] + "\n\n[Content truncated due to length...]"

                    extracted_files.append({
                        'filename': filename,
                        'size': len(file_content),
                        'content': content,
                        'word_count': len(content.split())
                    })

                except Exception as e:
                    errors.append(f'{filename}: Failed to extract content - {str(e)}')

            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        if not extracted_files and errors:
            return jsonify({
                'error': 'No files could be processed',
                'details': errors
            }), 400

        response_data = {
            'success': True,
            'files': extracted_files,
            'total_files': len(extracted_files)
        }

        if errors:
            response_data['partial_success'] = True
            response_data['errors'] = errors

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error extracting file content: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/orchestrator/process', methods=['POST'])
@limiter.limit("30 per minute")
def orchestrate_request():
    """
    MAHER Orchestrator Agent
    Analyzes user input, selects appropriate specialized agents,
    coordinates execution, and synthesizes responses
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_input = data.get('input', '')
        if not user_input:
            return jsonify({'error': 'Input is required'}), 400

        # Get all published agents from database
        db = SessionLocal()
        try:
            published_agents = db.query(Agent).filter(
                Agent.status == AgentStatus.PUBLISHED
            ).all()

            # Format agents for orchestrator decision
            agents_list = []
            for agent in published_agents:
                agents_list.append({
                    'id': agent.agent_id,
                    'name': agent.name,
                    'description': agent.description,
                    'category': agent.category
                })

        finally:
            db.close()

        if not agents_list:
            return jsonify({'error': 'No agents available'}), 500


        # Step 1: Orchestrator analyzes task and selects agents
        
        # Add a default 'General Maintenance' option to the list for robust fallback
        agents_for_selection = agents_list + [{
            'id': 'general-maintenance',
            'name': 'General Maintenance Expert',
            'description': 'Handles general maintenance queries, troubleshooting, and broad technical questions not covered by specific agents.',
            'category': 'maintenance'
        }]

        orchestrator_prompt = f"""You are the MAHER Orchestrator Agent. Your job is to analyze user requests and determine which specialized agents should handle the task.

Available Agents:
{json.dumps(agents_for_selection, indent=2)}

User Request: "{user_input}"

Analyze this request and decide:
1. Can this be handled by a specific agent?
2. If NO specific agent matches well, select 'general-maintenance'.
3. If multiple agents are needed, list them all.

Respond in JSON format:
{{
  "strategy": "single" or "multi",
  "selected_agents": [
    {{
      "agent_id": "agent-id",
      "agent_name": "Agent Name",
      "subtask": "Specific task for this agent"
    }}
  ],
  "reasoning": "Brief explanation of why these agents were selected"
}}"""

        logger.info(f"Orchestrator analyzing request: {user_input[:100]}...")

        # Use unified model client for orchestrator decision
        orch_result = model_client.generate(
            prompt=orchestrator_prompt,
            temperature=0.3,
            response_mime_type='application/json',
        )

        if not orch_result.success:
            logger.warning("Orchestrator LLM failed, falling back to General Maintenance")
            decision = {
                "strategy": "single",
                "selected_agents": [{
                    "agent_id": "general-maintenance",
                    "agent_name": "General Maintenance Expert",
                    "subtask": user_input
                }],
                "reasoning": "Fallback due to orchestrator service failure."
            }
        else:
            try:
                decision = json.loads(orch_result.text)
            except json.JSONDecodeError:
                logger.error("Orchestrator returned invalid JSON, falling back")
                decision = {
                    "strategy": "single",
                    "selected_agents": [{
                        "agent_id": "general-maintenance",
                        "agent_name": "General Maintenance Expert",
                        "subtask": user_input
                    }],
                    "reasoning": "Fallback due to invalid JSON response."
                }

        # If orchestrator returned empty selection, enforce fallback
        if not decision.get('selected_agents'):
             decision['selected_agents'] = [{
                "agent_id": "general-maintenance",
                "agent_name": "General Maintenance Expert",
                "subtask": user_input
            }]

        logger.info(f"Orchestrator decision: {decision.get('strategy')} strategy with {len(decision.get('selected_agents', []))} agent(s)")

        # Step 2: Execute selected agents
        agent_responses = []
        db = SessionLocal()
        try:
            for selected in decision.get('selected_agents', []):
                agent_id = selected.get('agent_id')
                subtask = selected.get('subtask', user_input)

                # Special handling for General Maintenance Fallback
                if agent_id == 'general-maintenance':
                    logger.info("Executing General Maintenance Fallback")
                    fallback_system_prompt = "You are MAHER, a versatile Maintenance Expert for Saudi Aramco. You help with general troubleshooting, safety procedures, and technical inquiries. Providing accurate, safety-first advice."
                    
                    bg_result = model_client.generate(
                        prompt=subtask,
                        system_instruction=fallback_system_prompt
                    )
                    
                    if bg_result.success:
                         agent_responses.append({
                            'agent_name': 'General Maintenance Expert',
                            'agent_id': 'general-maintenance',
                            'subtask': subtask,
                            'response': bg_result.text
                        })
                    continue

                # Get agent details from database
                agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
                if not agent:
                    logger.warning(f"Agent ID {agent_id} not found in DB, skipping.")
                    continue

                # Call agent with its system prompt via unified model client
                logger.info(f"Executing agent: {agent.name}")

                agent_result_obj = model_client.generate(
                    prompt=subtask,
                    system_instruction=agent.system_prompt,
                )

                if not agent_result_obj.success:
                    logger.warning(f"Agent {agent.name} failed: {agent_result_obj.error}")
                    continue

                agent_result = agent_result_obj.text

                agent_responses.append({
                    'agent_name': agent.name,
                    'agent_id': agent.agent_id,
                    'subtask': subtask,
                    'response': agent_result
                })

        finally:
            db.close()

        # Step 3: Synthesize responses
        if not agent_responses:
             return jsonify({'error': 'No agents were able to process your request.'}), 500

        if len(agent_responses) == 1:
            # Single agent - return its response directly with context
            final_response = f"**{agent_responses[0]['agent_name']}** handled your request:\n\n{agent_responses[0]['response']}"
        else:
            # Multiple agents - synthesize
            synthesis_prompt = f"""You are MAHER, the orchestration coordinator. Multiple specialized agents have processed different aspects of the user's request. Your job is to synthesize their responses into a single, coherent, and professional answer.

Original User Request: "{user_input}"

Agent Responses:
"""
            for resp in agent_responses:
                synthesis_prompt += f"\n**{resp['agent_name']}** (Task: {resp['subtask']}):\n{resp['response']}\n"

            synthesis_prompt += """

Create a unified response that:
1. Integrates all agent insights seamlessly
2. Maintains a professional, engineering-focused tone
3. Clearly attributes different aspects to relevant expertise areas
4. Provides actionable conclusions

Present as MAHER, the central AI coordinator."""

            logger.info("Synthesizing multi-agent responses...")

            synth_result = model_client.generate(
                prompt=synthesis_prompt,
                system_instruction="You are MAHER, a Specialized Maintenance Assistant from Saudi Aramco's Corporate Maintenance Services Department. You coordinate multiple AI specialists and present unified responses professionally.",
            )

            if not synth_result.success:
                final_response = "\n\n---\n\n".join([r['response'] for r in agent_responses])
            else:
                final_response = synth_result.text

        # Generate follow-up questions and suggested actions
        try:
            from follow_up_generator import generate_follow_up_questions
            from action_suggester import generate_suggested_actions
            
            # Get the primary agent's category for context
            primary_agent_category = agent_responses[0]['agent_name'] if agent_responses else 'General'
            
            # Generate follow-up questions
            follow_up_questions = generate_follow_up_questions(
                user_input=user_input,
                agent_response=final_response,
                agent_category=primary_agent_category,
                model_client=model_client,
                max_questions=3
            )
            
            # Generate suggested actions
            suggested_actions = generate_suggested_actions(
                content=final_response,
                agent_category=primary_agent_category,
                agent_name=agent_responses[0]['agent_name'] if agent_responses else 'Agent'
            )
            
        except Exception as e:
            logger.error(f"Error generating follow-ups/actions: {str(e)}")
            follow_up_questions = []
            suggested_actions = []

        # Return enhanced orchestrated response
        return jsonify({
            'success': True,
            'response': final_response,
            'follow_up_questions': follow_up_questions,
            'suggested_actions': suggested_actions,
            'orchestration': {
                'strategy': decision.get('strategy'),
                'agents_used': [{'name': r['agent_name'], 'id': r['agent_id']} for r in agent_responses],
                'reasoning': decision.get('reasoning')
            }
        }), 200

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in orchestrator: {str(e)}")
        return jsonify({'error': 'Failed to parse orchestrator decision'}), 500

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed in orchestrator: {str(e)}")
        return jsonify({'error': 'Failed to communicate with AI service'}), 503

    except Exception as e:
        logger.error(f"Unexpected error in orchestrator: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/documents/generate', methods=['POST'])
@limiter.limit("20 per minute")
def generate_document_on_demand():
    """
    Generate document on-demand when user clicks action
    
    Request body:
        {
            "content": "The agent's response text",
            "format": "pdf" | "word" | "excel",
            "title": "Document Title",
            "metadata": {
                "agent_name": "Maintenance Agent",
                "generated_at": "2026-02-03T22:00:00"
            }
        }
    
    Returns:
        {
            "success": true,
            "download_url": "/api/documents/download/checklist_20260203.pdf",
            "filename": "checklist_20260203.pdf",
            "format": "pdf",
            "size": 45678
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        content = data.get('content', '')
        format = data.get('format', 'pdf')
        title = data.get('title', 'Document')
        metadata = data.get('metadata', {})
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Validate format
        if format.lower() not in ['pdf', 'word', 'docx', 'excel', 'xlsx']:
            return jsonify({'error': f'Unsupported format: {format}'}), 400
        
        # Generate document
        from document_generator import generate_document
        
        logger.info(f"Generating {format} document: {title[:50]}...")
        
        result = generate_document(
            content=content,
            format=format,
            title=title,
            metadata=metadata
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'download_url': result['download_url'],
                'filename': result['filename'],
                'format': format,
                'size': result.get('size', 0)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Document generation failed')
            }), 500
            
    except Exception as e:
        logger.error(f"Document generation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/documents/download/<filename>', methods=['GET'])
def download_document(filename):
    """
    Serve generated documents for download
    
    Args:
        filename: Name of the file to download
    
    Returns:
        File download response
    """
    try:
        # Security: Validate filename (prevent path traversal)
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        # Get file path
        docs_dir = os.path.join(tempfile.gettempdir(), 'maher_docs')
        file_path = os.path.join(docs_dir, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Determine content type
        if filename.endswith('.pdf'):
            mimetype = 'application/pdf'
        elif filename.endswith('.docx'):
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.endswith('.xlsx'):
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            mimetype = 'application/octet-stream'
        
        logger.info(f"Serving document: {filename}")
        
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500



@app.route('/api/models', methods=['GET'])
@limiter.limit("10 per minute")
def list_models():
    """
    Get available AI model providers and their status
    """
    try:
        provider_status = model_client.get_status()
        return jsonify({
            'providers': provider_status,
            'active': model_client.get_active_provider(),
        }), 200

    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        return jsonify({'error': 'Failed to fetch models'}), 500


# ============================================================================
# Skills Orchestrator Endpoints  (GPT-OSS native function calling)
# ============================================================================

@app.route('/api/skills-orchestrator/process', methods=['POST'])
@limiter.limit("30 per minute")
def skills_orchestrator_process():
    """
    Process a request through the Skills Orchestrator.

    The orchestrator semantically retrieves the 3-7 most relevant skill
    schemas, injects only those into the 32 K context, and lets GPT-OSS
    select and call skills via native function calling (ReAct loop).

    Request body:
        {
            "input": "Generate a maintenance checklist for pump P-101",
            "history": [{"role": "user", "content": "..."}, ...],  // optional
            "system_prompt": "...",   // optional override
            "stream": false           // optional
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_input = data.get('input', '').strip()
        if not user_input:
            return jsonify({'error': 'input is required'}), 400

        history       = data.get('history', [])
        system_prompt = data.get('system_prompt', '')

        orchestrator = get_skills_orchestrator()
        if orchestrator is None:
            return jsonify({'error': 'SkillsOrchestrator unavailable'}), 503

        result = orchestrator.process(
            user_message=user_input,
            conversation_history=history,
            system_prompt=system_prompt,
        )

        return jsonify(result)

    except Exception as exc:
        logger.error(f"skills_orchestrator_process error: {exc}", exc_info=True)
        return jsonify({'error': str(exc)}), 500


@app.route('/api/skills-orchestrator/reload', methods=['POST'])
@limiter.limit("10 per minute")
def skills_orchestrator_reload():
    """
    Hot-reload the skills registry without restarting the server.
    Call this after AI Studio publishes a new skill.
    Requires admin session.
    """
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    orchestrator = get_skills_orchestrator()
    if orchestrator is None:
        return jsonify({'error': 'SkillsOrchestrator unavailable'}), 503

    result = orchestrator.reload_skills()
    return jsonify(result)


# ============================================================================
# Hybrid Orchestrator Endpoints
# ============================================================================

@app.route('/api/hybrid-orchestrator/process', methods=['POST'])
@limiter.limit("30 per minute")
def hybrid_orchestrator_process():
    """
    Process request through Hybrid Orchestrator
    Automatically routes to AI Agents, Workflows, or Tools
    """
    try:
        from hybrid_orchestrator import HybridOrchestrator
        import asyncio

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_input = data.get('input', '')
        if not user_input:
            return jsonify({'error': 'Input is required'}), 400

        # Initialize orchestrator with model client
        orchestrator = HybridOrchestrator(model_client=model_client)

        # Process request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(orchestrator.process_request(user_input))
        finally:
            loop.close()

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in hybrid orchestrator: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process request',
            'details': str(e)
        }), 500


@app.route('/api/hybrid-orchestrator/process-with-files', methods=['POST'])
@limiter.limit("30 per minute")
def hybrid_orchestrator_process_with_files():
    """
    Process request through Hybrid Orchestrator with file attachments
    Handles file uploads and passes file paths to document processing tools

    Form data:
        - input: Text description of what to do
        - files: One or more file attachments
    """
    try:
        from hybrid_orchestrator import HybridOrchestrator
        import asyncio
        import tempfile
        import shutil

        # Get user input from form data
        user_input = request.form.get('input', '')
        if not user_input:
            return jsonify({'error': 'Input is required'}), 400

        # Get uploaded files
        uploaded_files = request.files.getlist('files')

        # Create temp directory for uploaded files
        temp_dir = tempfile.mkdtemp(prefix='maher_orchestrator_')
        file_paths = []
        file_info = []

        try:
            # Save uploaded files
            for uploaded_file in uploaded_files:
                if uploaded_file.filename:
                    filename = secure_filename(uploaded_file.filename)
                    file_path = os.path.join(temp_dir, filename)
                    uploaded_file.save(file_path)
                    file_paths.append(file_path)

                    file_size = os.path.getsize(file_path)
                    file_ext = os.path.splitext(filename)[1].lower()

                    file_info.append({
                        'filename': filename,
                        'path': file_path,
                        'size': file_size,
                        'extension': file_ext
                    })

            if not file_paths:
                return jsonify({'error': 'No files were uploaded'}), 400

            enhanced_input = f"""{user_input}

Files provided:
{chr(10).join([f"- {info['filename']} ({info['extension']}, {info['size']} bytes) at path: {info['path']}" for info in file_info])}

Use the file paths above to process the documents."""

            logger.info(f"Processing orchestrator request with {len(file_paths)} files")
            logger.info(f"Files: {[f['filename'] for f in file_info]}")

            # Initialize orchestrator with model client
            orchestrator = HybridOrchestrator(model_client=model_client)

            # Process request
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(orchestrator.process_request(enhanced_input))
            finally:
                loop.close()

            result['files_processed'] = file_info
            return jsonify(result), 200

        finally:
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temp directory: {temp_dir}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp directory {temp_dir}: {cleanup_error}")

    except Exception as e:
        logger.error(f"Error in hybrid orchestrator with files: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process request with files',
            'details': str(e)
        }), 500


@app.route('/api/hybrid-orchestrator/feedback', methods=['POST'])
@limiter.limit("50 per hour")
def submit_feedback():
    """
    Submit feedback for orchestrator performance
    Request body:
        - request_id: The request ID to provide feedback for
        - rating: Rating from 1-5 stars
        - feedback_text: Optional feedback text
    """
    try:
        from hybrid_orchestrator import HybridOrchestrator

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        request_id = data.get('request_id')
        rating = data.get('rating')

        if not request_id:
            return jsonify({'error': 'request_id is required'}), 400

        if rating is None or not (1 <= rating <= 5):
            return jsonify({'error': 'rating must be between 1 and 5'}), 400

        feedback_text = data.get('feedback_text', '')

        # Initialize orchestrator
        orchestrator = HybridOrchestrator()

        # Save feedback
        result = orchestrator.save_feedback(request_id, rating, feedback_text)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit feedback',
            'details': str(e)
        }), 500


@app.route('/api/hybrid-orchestrator/feedback/stats', methods=['GET'])
@limiter.limit("20 per minute")
def get_feedback_stats():
    """
    Get feedback statistics
    """
    try:
        from hybrid_orchestrator import HybridOrchestrator

        # Initialize orchestrator
        orchestrator = HybridOrchestrator()

        # Get statistics
        stats = orchestrator.get_feedback_statistics()

        return jsonify({
            'success': True,
            'statistics': stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get feedback statistics',
            'details': str(e)
        }), 500


# ============================================================================
# Plan-Execute-Verify (PEV) Orchestrator Endpoints - NEW ARCHITECTURE
# ============================================================================

@app.route('/api/pev-orchestrator/process', methods=['POST'])
@limiter.limit("30 per minute")
def pev_orchestrator_process():
    """
    Process request through Plan-Execute-Verify (PEV) Orchestrator
    NEW: Implements hallucination prevention with rigorous verification

    Architecture: User Input → Planner → Executor → Verifier → Response
    With loop-back if verification fails (max 2 retries)

    Request body:
        - input: User's request
        - user_id: Optional user ID
        - user_role: Optional user role (for context)

    Returns:
        - answer: Verified, hallucination-free response
        - verification: Verification metrics (confidence, completeness, etc.)
        - trace_id: For feedback tracking
    """
    try:
        from pev_orchestrator import PEVOrchestrator

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_input = data.get('input', '')
        if not user_input:
            return jsonify({'error': 'Input is required'}), 400

        user_id = data.get('user_id')
        user_role = data.get('user_role', 'User')

        # Initialize PEV orchestrator with model client
        orchestrator = PEVOrchestrator(model_client=model_client)

        # Process request through Plan-Execute-Verify cycle
        result = orchestrator.process_request(
            user_input=user_input,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in PEV orchestrator: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process request',
            'details': str(e)
        }), 500


@app.route('/api/pev-orchestrator/process-with-files', methods=['POST'])
@limiter.limit("30 per minute")
def pev_orchestrator_process_with_files():
    """
    Process request through PEV Orchestrator with file attachments
    NEW: Combines file processing with hallucination prevention

    Form data:
        - input: Text description of what to do
        - files: One or more file attachments
        - user_id: Optional user ID
        - user_role: Optional user role
    """
    try:
        from pev_orchestrator import PEVOrchestrator
        import tempfile
        import shutil

        # Get user input from form data
        user_input = request.form.get('input', '')
        if not user_input:
            return jsonify({'error': 'Input is required'}), 400

        user_id = request.form.get('user_id')
        user_role = request.form.get('user_role', 'User')

        # Get uploaded files
        uploaded_files = request.files.getlist('files')

        # Create temp directory for uploaded files
        temp_dir = tempfile.mkdtemp(prefix='maher_pev_')
        file_paths = []
        file_info = []

        try:
            # Save uploaded files
            for uploaded_file in uploaded_files:
                if uploaded_file.filename:
                    filename = secure_filename(uploaded_file.filename)
                    file_path = os.path.join(temp_dir, filename)
                    uploaded_file.save(file_path)

                    file_paths.append(file_path)
                    file_info.append({
                        'filename': filename,
                        'extension': os.path.splitext(filename)[1],
                        'size': os.path.getsize(file_path)
                    })

            # Enhance input with file context
            enhanced_input = f"""{user_input}

Files provided:
{chr(10).join([f'- {f["filename"]} ({f["extension"]}, {f["size"]} bytes) at path: {p}' for f, p in zip(file_info, file_paths)])}

Use the file paths above to process the documents."""

            logger.info(f"Processing PEV request with {len(file_paths)} files")

            # Initialize PEV orchestrator with model client
            orchestrator = PEVOrchestrator(model_client=model_client)

            # Process request
            result = orchestrator.process_request(
                user_input=enhanced_input,
                user_id=user_id,
                user_role=user_role
            )

            return jsonify(result), 200

        finally:
            # Cleanup temp directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp directory {temp_dir}: {cleanup_error}")

    except Exception as e:
        logger.error(f"Error in PEV orchestrator with files: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process request with files',
            'details': str(e)
        }), 500


@app.route('/api/pev-orchestrator/metrics', methods=['GET'])
@limiter.limit("20 per minute")
def pev_orchestrator_metrics():
    """
    Get PEV orchestrator performance metrics

    Returns metrics like:
    - Hallucination rate
    - Average confidence scores
    - Verification statistics
    """
    try:
        # TODO: Implement metrics collection
        # For now, return placeholder
        return jsonify({
            'success': True,
            'metrics': {
                'hallucination_rate': 0.0,
                'average_confidence': 0.85,
                'total_requests': 0,
                'verification_passes': 0,
                'verification_retries': 0
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting PEV metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get metrics',
            'details': str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors by serving the React app (for client-side routing)"""
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong. Please try again later.'
    }), 500


# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Don't cache API responses
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

    return response


# ============================================================================
# Direct Chat Endpoint
# ============================================================================

@app.route('/api/chat/generate', methods=['POST'])
@limiter.limit("10 per minute")
def chat_generate():
    """
    Direct chat generation endpoint to support client.ts
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        contents = data.get('contents', [])
        system_instruction = data.get('systemInstruction')
        
        # Extract prompt from Gemini-style contents
        prompt = ""
        if contents:
            # Get the last user message
            for content in reversed(contents):
                if content.get('role') == 'user':
                    for part in content.get('parts', []):
                        prompt += part.get('text', '')
                    break
        
        if not prompt:
            # Fallback for simple prompt
            prompt = data.get('prompt', '')

        if not prompt:
             return jsonify({'error': 'No prompt found'}), 400

        # Generate response
        response = model_client.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            contents=contents 
        )

        if response.success:
            # Format response for client.ts (Gemini format)
            return jsonify({
                "candidates": [{
                    "content": {
                        "parts": [{"text": response.text}],
                        "role": "model"
                    },
                    "finishReason": "STOP",
                    "index": 0
                }]
            }), 200
        else:
            return jsonify({'error': response.error}), 500

    except Exception as e:
        logger.error(f"Chat generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Development server - DO NOT use in production
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
