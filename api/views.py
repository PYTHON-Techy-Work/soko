from flask import Flask, jsonify, request, make_response
from flask_restful import Api

app = Flask(__name__)
api = Api(app)



users = [
    {
        'id': 1,
        'name': 'James',
        'email': 'njugunanduati@gmail.com'
    },
    {
        'id': 2,
        'name': 'Paul',
        'email': 'paul@gmail.com'
    }
]
@app.route('/soko/api/v1.0/users', methods=['GET'])
def get_tasks():
    return make_response(jsonify({'users': users}))

if __name__ == '__main__':
    app.run(debug=True)