import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from app.api.routes import api_bp
from app.core.constants import UPLOADS_DIR, REPORTS_DIR, LOGS_DIR
from app.core.logging import setup_logging
from app.core.lifecycle import run_startup_hooks

logger = setup_logging('defect_agent_api')

def create_app():
    app = Flask(__name__, static_folder='web', static_url_path='')
    CORS(app)
    
    app.config['UPLOAD_FOLDER'] = UPLOADS_DIR
    app.config['REPORT_FOLDER'] = REPORTS_DIR
    
    run_startup_hooks()
    
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return send_from_directory('web', 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory('web', path)
    
    logger.info("Flask应用启动成功")
    
    return app

if __name__ == '__main__':
    app = create_app()
    host = os.environ.get('APP_HOST', '0.0.0.0')
    port = int(os.environ.get('APP_PORT', 5000))
    debug = os.environ.get('APP_DEBUG', 'false').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)