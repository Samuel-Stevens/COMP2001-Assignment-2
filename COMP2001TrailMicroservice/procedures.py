from flask import Flask, request, jsonify
from __init__ import db
from __init__ import app
from sqlalchemy import text
from authentication import token_required, role_required

@app.route('/users/<user_id>', methods=['GET'])
def fetch_user_by_id(user_id):
    try:
        query = text("EXEC [CW2].[ReadUser] @UserID = :UserID")
        result = db.session.execute(query, {'UserID': user_id})
        users = [dict(row._mapping) for row in result.fetchall()]
        
        if not users:
            return jsonify({"message": "User not found"}), 404
        
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": "Cant fetch user", "error": str(e)}), 500


@app.route('/users', methods=['GET'])
def fetch_all_users():
    try:
        query = text("EXEC [CW2].[ReadUser]")
        result = db.session.execute(query)
        users = [dict(row._mapping) for row in result.fetchall()]
        
        if not users:
            return jsonify({"message": "User not found"}), 404
        
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": "Cant fetch user", "error": str(e)}), 500


@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not all(key in data for key in ['Username', 'Email', 'Password', 'Role']):
            return jsonify({"message": "All user fields are required"}), 400

        query = text("""
            EXEC [CW2].[CreateUser] 
            @Username = :Username, @Email = :Email, @Password = :Password, @Role = :Role
        """)
        db.session.execute(query, data)
        db.session.commit()
        return jsonify({"message": "New User created successfully!"}), 201
    except Exception as e:
        return jsonify({"message": "Cant create user", "error": str(e)}), 500


@app.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    try:
        data = request.get_json()
        query = text("""
            EXEC [CW2].[UpdateUser] 
            @UserID = :UserID, @Username = :Username, @Email = :Email, @Password = :Password, @Role = :Role
        """)
        db.session.execute(query, {'UserID': user_id, **data})
        db.session.commit()
        return jsonify({"message": "User updated successfully!"}), 200
    except Exception as e:
        return jsonify({"message": "Cant update user", "error": str(e)}), 500


@app.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    try:
        query = text("EXEC [CW2].[DeleteUser] @UserID = :UserID")
        db.session.execute(query, {'UserID': user_id})
        db.session.commit()
        return jsonify({"message": "User deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"message": "Cant delete user", "error": str(e)}), 500


    