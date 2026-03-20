"""
WSGI entry point for production deployment with Waitress
"""

import os
import sys
import logging
from waitress import serve

# Add current directory to sys.path to ensure 'app' and siblings can be imported
# This fixes "ModuleNotFoundError: No module named 'app'" in embeddable python
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
except Exception as e:
    print(f"Warning: Could not set sys.path: {e}")

from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maher_ai.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """
    Start the production server using Waitress
    """
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    threads = int(os.environ.get('THREADS', 4))

    logger.info(f"Starting MAHER AI Backend Server")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Threads: {threads}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")

    try:
        # Check if SSL Certificates exist in the backend folder
        cert_file = os.path.join(current_dir, "server.crt")
        key_file = os.path.join(current_dir, "server.key")
        
        has_ssl = os.path.exists(cert_file) and os.path.exists(key_file)

        if has_ssl:
            logger.info("SSL certificates found. Starting CherryPy WSGI Server on HTTPS...")
            import cherrypy
            
            cherrypy.config.update({
                'server.socket_host': host,
                'server.socket_port': port,
                'server.ssl_module': 'builtin',
                'server.ssl_certificate': cert_file,
                'server.ssl_private_key': key_file,
                'server.thread_pool': threads,
            })
            
            # Mount the WSGI app
            cherrypy.tree.graft(app, '/')
            
            # Start the web server
            cherrypy.engine.start()
            logger.info(f"CherryPy serving on https://{host}:{port}")
            cherrypy.engine.block()
        else:
            logger.info("No SSL certificates found. Starting Waitress WSGI Server on HTTP...")
            serve(
                app,
                host=host,
                port=port,
                threads=threads,
                url_scheme='http',  # Default to HTTP if no certs
                channel_timeout=120,
                cleanup_interval=30,
                asyncore_use_poll=True,
                _quiet=False
            )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise


if __name__ == '__main__':
    main()
