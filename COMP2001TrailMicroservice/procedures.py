from flask import Flask, request, jsonify
from __init__ import db
from __init__ import app
from sqlalchemy import text
from authentication import token_required

#Start of User CRUD operations
@app.route('/Users/<user_id>', methods=['GET'])
def fetch_user_by_id(user_id):
    try:
        query = text("EXEC [CW2].[ReadUser] @UserID = :UserID")
        result = db.session.execute(query, {'UserID': user_id})
        users = [dict(row._mapping) for row in result.fetchall()]
        
        if not users:
            return ({"message": "User not found"}), 404
        
        return jsonify(users), 200
    except Exception as e:
        return ({"message": "Cant fetch user", "error": str(e)}), 500


@app.route('/Users', methods=['GET'])
def fetch_all_users():
    try:
        query = text("SELECT * FROM CW2.USERS")
        result = db.session.execute(query)
        users = [dict(row._mapping) for row in result.fetchall()]
        
        if not users:
            return ({"message": "User not found"}), 404
        
        return jsonify(users), 200
    except Exception as e:
        return ({"message": "Cant fetch user", "error": str(e)}), 500


@app.route('/Users/create', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        required_fields = ['Username', 'Email', 'Password', 'Role']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return ({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400

       
        query = text("""
            EXEC [CW2].[CreateUser] 
            @Username = :Username, @Email = :Email, @Password = :Password, @Role = :Role
        """)
        db.session.execute(query, data)
        db.session.commit()

        return ({"message": "New User created successfully!"}), 201

    except Exception as e:
        
        return ({"message": "Cannot create user", "error": str(e)}), 500


@app.route('/Users/update/<user_id>', methods=['PUT'])
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
        return ({"message": "User updated successfully!"}), 200
    except Exception as e:
        return ({"message": "Cant update user", "error": str(e)}), 500


@app.route('/Users/delete/<user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    try:
        query = text("EXEC [CW2].[DeleteUser] @UserID = :UserID")
        db.session.execute(query, {'UserID': user_id})
        db.session.commit()
        return ({"message": "User deleted successfully!"}), 200
    except Exception as e:
        return ({"message": "Cant delete user", "error": str(e)}), 500

#Start of Trail CRUD operations

@app.route('/Trails', methods=['GET'])
def fetch_all_trails():
    try:
        query = text("SELECT * FROM CW2.TRAIL")
        result = db.session.execute(query)
        trails = [dict(row._mapping) for row in result.fetchall()]
        
        if not trails:
            return ({"message": "Trail not found"}), 404
        
        return (trails), 200
    except Exception as e:
        return ({"message": "Cant fetch trail", "error": str(e)}), 500

@app.route('/Trails/<trail_id>', methods=['GET'])
def fetch_trail_by_id(trail_id):
    try:
        query = text("EXEC [CW2].[ReadTrail] @TrailID = :TrailID")
        result = db.session.execute(query, {'TrailID': trail_id})
        trails = [dict(row._mapping) for row in result.fetchall()]
        
        if not trails:
            return ({"message": "Trail not found"}), 404
        
        return (trails), 200
    except Exception as e:
        return ({"message": "Cant fetch trail", "error": str(e)}), 500

@app.route('/Trails/create', methods=['POST'])
@token_required
def create_trail():
    try:
        data = request.get_json()

        # Define required fields
        trail_fields = [
            'TrailName', 'TrailSummary', 'TrailDescription',
            'Difficulty', 'Location', 'Length', 'ElevationGain', 'RouteType',
            'OwnerID'
        ]
        coordinate_fields = [
            f'Pt{i}_{suffix}' for i in range(1, 6) for suffix in ['Lat', 'Long', 'Desc']
        ]
        required_fields = trail_fields + coordinate_fields

        # Validate required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return ({
                "message": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        
        data['UserID'] = data['OwnerID']

        # Construct SQL query
        query = text(f"""
            EXEC [CW2].[CreateTrail] 
            {", ".join([f"@{field} = :{field}" for field in required_fields])}
        """)

        # Execute query
        db.session.execute(query, data)
        db.session.commit()

        return ({"message": "Trail created successfully!"}), 201

    except Exception as e:
        return ({"message": "Cannot create trail", "error": str(e)}), 500



@app.route('/Trails/update/<trail_id>', methods=['PUT'])
@token_required
def update_trail(TrailID):
    try:
        
        data = request.get_json()

        # Define required fields
        trail_fields = [
            'TrailName', 'TrailSummary', 'TrailDescription', 'Difficulty',
            'Location', 'Length', 'ElevationGain', 'RouteType', 'OwnerID'
        ]
        coordinate_fields = [
            f'Pt{i}_{suffix}' for i in range(1, 6) for suffix in ['Desc', 'Lat', 'Long']
        ]
        required_fields = trail_fields + coordinate_fields

        # Validate required fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return ({
                "message": "Missing required fields",
                "missing_fields": missing_fields
            }), 400

        
        data['TrailID'] = TrailID
        data['UserID'] = data['OwnerID']  

        
        query = text("""
            EXEC [CW2].[UpdateTrail]
            @TrailID = :TrailID, @TrailName = :TrailName, @TrailSummary = :TrailSummary,
            @TrailDescription = :TrailDescription, @Difficulty = :Difficulty,
            @Location = :Location, @Length = :Length, @ElevationGain = :ElevationGain,
            @RouteType = :RouteType, @OwnerID = :OwnerID,
            @Pt1_Desc = :Pt1_Desc, @Pt1_Lat = :Pt1_Lat, @Pt1_Long = :Pt1_Long,
            @Pt2_Desc = :Pt2_Desc, @Pt2_Lat = :Pt2_Lat, @Pt2_Long = :Pt2_Long,
            @Pt3_Desc = :Pt3_Desc, @Pt3_Lat = :Pt3_Lat, @Pt3_Long = :Pt3_Long,
            @Pt4_Desc = :Pt4_Desc, @Pt4_Lat = :Pt4_Lat, @Pt4_Long = :Pt4_Long,
            @Pt5_Desc = :Pt5_Desc, @Pt5_Lat = :Pt5_Lat, @Pt5_Long = :Pt5_Long
        """)

        db.session.execute(query, data)
        db.session.commit()

        return ({"message": "Trail updated successfully!"}), 200

    except Exception as e:
       
        return ({"message": "Cannot update trail", "error": str(e)}), 500




@app.route('/Trail/delete/<TrailID>', methods=['DELETE'])
@token_required
def delete_trail(TrailID):
    try:
        query = text("EXEC [CW2].[DeleteTrail] @TrailID = :TrailID")
        db.session.execute(query, {'TrailID': TrailID})
        db.session.commit()
        return ({"message": "Trail deleted successfully!"}), 200
    except Exception as e:
        return ({"message": "Cant delete Trail", "error": str(e)}), 500




#Start of Feature CRUD operations
@app.route('/features/<feature_id>', methods=['GET'])
def fetch_feature_by_id(feature_id):
    try:
        query = text("EXEC [CW2].[ReadFeature] @TrailFeatureID = :TrailFeatureID")
        result = db.session.execute(query, {'TrailFeatureID': feature_id})
        features = [dict(row._mapping) for row in result.fetchall()]
        
        if not features:
            return ({"message": "Feature not found"}), 404
        
        return (features), 200
    except Exception as e:
        return ({"message": "Cant fetch feature", "error": str(e)}), 500


@app.route('/features/create', methods=['POST'])
@token_required
def create_feature():
    try:
        data = request.get_json()
        if not 'TrailFeature' in data:
            return ({"message": "TrailFeature field is required"}), 400

        query = text("""
            EXEC [CW2].[CreateFeature] 
            @TrailFeature = :TrailFeature
        """)
        db.session.execute(query, data)
        db.session.commit()
        return ({"message": "Feature created successfully!"}), 201
    except Exception as e:
        return ({"message": "Cant create feature", "error": str(e)}), 500


@app.route('/features/update/<featureid>', methods=['PUT'])
@token_required
def update_Feature(TrailFeatureID):
    try:
        data = request.get_json()
        query = text("""
            EXEC [CW2].[UpdateFeature] 
            @TrailFeatureID = :TrailFeatureID, @TrailFeature = :TrailFeature
        """)
        db.session.execute(query, {'TrailFeatureID': TrailFeatureID, **data})
        db.session.commit()
        return ({"message": "Feature updated successfully!"}), 200
    except Exception as e:
        return ({"message": "Feature update user", "error": str(e)}), 500


@app.route('/features/delete/<feature_id>', methods=['DELETE'])
@token_required
def delete_feature(feature_id):
    try:
        query = text("EXEC [CW2].[DeleteFeature] @TrailFeatureID = :TrailFeatureID")
        db.session.execute(query, {'TrailFeatureID': feature_id})
        db.session.commit()
        return ({"message": "Feature deleted successfully!"}), 200
    except Exception as e:
        return ({"message": "Cant delete feature", "error": str(e)}), 500

@app.route('/features', methods=['GET'])
def fetch_all_features():
    try:
        query = text("SELECT * FROM CW2.FEATURE")
        result = db.session.execute(query)
        features = [dict(row._mapping) for row in result.fetchall()]
        
        if not features:
            return ({"message": "Feature not found"}), 404
        
        return (features), 200
    except Exception as e:
        return ({"message": "Cant fetch feature", "error": str(e)}), 500


print("Routes registered in views.py:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == '__main__':
    app.run(debug=True)
    