"""
Production server startup script using Waitress
Run this file to start the MAHER AI server in production mode
"""

from waitress import serve
from app import app
import os
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maher_ai.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    threads = int(os.environ.get('THREADS', 4))

    logger.info(f"Starting MAHER AI Production Server on {host}:{port}")
    logger.info(f"Using {threads} threads")
    logger.info("Press CTRL+C to quit")

    # Serve the application using Waitress
    serve(
        app,
        host=host,
        port=port,
        threads=threads,
        url_scheme='https' if os.environ.get('USE_HTTPS', 'false').lower() == 'true' else 'http',
        # Connection settings
        connection_limit=1000,
        cleanup_interval=30,
        channel_timeout=120,
        # Performance tuning
        asyncore_use_poll=True,
        # Logging
        _quiet=False
    )
