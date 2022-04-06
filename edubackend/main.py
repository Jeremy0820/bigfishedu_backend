from edubackend import create_flask_app
from flask_cors import CORS
from common.settings.default import DefaultConfig

app = create_flask_app(DefaultConfig)
CORS(app)

if __name__ == '__main__':
    app.run(debug=True)