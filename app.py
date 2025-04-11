from flask import Flask
from backend.routes.proportionings import bp as proportionings_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Regist blueprints
app.register_blueprint(proportionings_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

