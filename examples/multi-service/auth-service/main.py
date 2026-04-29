from flask import Flask
from app.auth.routes import auth_bp

app = Flask(__name__)

app.register_blueprint(auth_bp, url_prefix='/auth')


@app.route('/')
def root():
    return {"service": "auth", "status": "running"}


@app.route('/health')
def health():
    return {"status": "healthy"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
