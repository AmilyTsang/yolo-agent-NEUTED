import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.app import create_app
from app.core.logging import setup_logging

logger = setup_logging('run_server')

def main():
    logger.info("启动工业缺陷检测服务...")
    
    app = create_app()
    
    host = os.environ.get('APP_HOST', '0.0.0.0')
    port = int(os.environ.get('APP_PORT', 5000))
    debug = os.environ.get('APP_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"服务将在 http://{host}:{port} 启动")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()