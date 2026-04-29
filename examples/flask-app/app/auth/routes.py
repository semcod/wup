from flask import Blueprint, jsonify, request

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    return jsonify({"message": "Login successful", "user": data.get("username", "user")})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logout successful"})


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    return jsonify({"message": "User registered", "email": data.get("email", "")})


@auth_bp.route('/profile', methods=['GET'])
def profile():
    return jsonify({"id": 1, "username": "testuser", "email": "test@example.com"})


@auth_bp.route('/password', methods=['PUT'])
def change_password():
    data = request.get_json() or {}
    return jsonify({"message": "Password updated"})
