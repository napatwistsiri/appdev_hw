from flask import Flask, jsonify, request
from flask_basicauth import BasicAuth
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb+srv://napat:7233@cluster0.8di2w4x.mongodb.net/?retryWrites=true&w=majority') 

db = client['students']     
collection = db['std_info']   

app.config['BASIC_AUTH_USERNAME'] = '1'  
app.config['BASIC_AUTH_PASSWORD'] = '1'   

basic_auth = BasicAuth(app)


formatted_students = [
    {"_id": student["_id"], "fullname": student["fullname"], "major": student["major"], "gpa": student["gpa"]}
    for student in collection.find()
]

@app.route('/')
def welcome():
    return "Welcome to Student Management API"


@app.route('/students', methods=['GET'])
@basic_auth.required
def get_all_students():
    return jsonify(formatted_students)


@app.route('/students/<int:std_id>', methods=['GET'])
@basic_auth.required
def get_student(std_id):
    student = next((s for s in formatted_students if s['_id'] == std_id), None)
    if student:
        return jsonify(student)
    else:
        return jsonify({"error": "Student not found"}), 404


@app.route('/students', methods=['POST'])
@basic_auth.required
def create_student():
    new_student_data = request.json

    
    existing_student = collection.find_one({"_id": new_student_data["_id"]})
    if existing_student:
        return jsonify({"error":"Cannot create new student"}),  500

    
    collection.insert_one(new_student_data)

    return jsonify(new_student_data), 200


@app.route('/students/<int:std_id>', methods=['PUT'])
@basic_auth.required
def update_student(std_id):
    
    student = collection.find_one({"_id": std_id})

    if student:
        
        new_student_data = request.json
        print(f"Received data for update: {new_student_data}")

        
        collection.update_one({"_id": std_id}, {"$set": new_student_data})

        
        updated_student = collection.find_one({"_id": std_id})
        print(f"Updated student data: {updated_student}")

        return jsonify(updated_student), 200
    else:
        return jsonify({"error": "Student not found"}), 404


@app.route('/students/<int:std_id>', methods=['DELETE'])
@basic_auth.required
def delete_student(std_id):
    global formatted_students
    student = next((s for s in formatted_students if s['_id'] == std_id), None)
    if student:
        formatted_students = [s for s in formatted_students if s['_id'] != std_id]
        return jsonify({"message": "Student deleted successfully"}), 200
    else:
        return jsonify({"error": "Student not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)