import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)


from edubackend import create_flask_app
from flask_cors import CORS
from common.settings.default import DefaultConfig

app = create_flask_app(DefaultConfig)
CORS(app)

if __name__ == '__main__':
    app.run(debug=True)