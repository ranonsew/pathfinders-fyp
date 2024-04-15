import sys
sys.path.append('./gunicorn-docker')

from app.app import create_app

from flask_cors import CORS

newApp = create_app()

CORS(newApp)

if __name__ == '__main__':
    newApp.run(host='0.0.0.0', port=5277, debug=True)
