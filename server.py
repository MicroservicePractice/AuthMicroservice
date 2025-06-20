import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

#config
server.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
server.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
server.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')  
server.config['MYSQL_DB'] = os.environ.get('MYSQL_DATABASE', 'test_db')
server.config['MYSQL_PORT'] = int(os.environ.get('AUTH_PORT', 3306))


@server.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return 'Could not verify', 401
    
    #check db for username and password
    cursor = mysql.connection.cursor()
    res = cursor.execute(
        "SELECT email, password FROM user WHERE email = %s", (auth.username,)
        )
    if res > 0:
        user_row = cursor.fetchone()
        email = user_row[0]
        password = user_row[1]
        if auth.username != email or auth.password != password:
            return 'Could not verify', 401
        else:
            return createJWT(auth.username, os.environ.get('JWT_SECRET'), True)
        
    else:
        return 'invalid credentials', 401
    

def createJWT(username, secret, is_admin):
    payload = {
        'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=0, seconds=45),
        'iat': datetime.datetime.now(tz=datetime.timezone.utc),
        'sub': username,
        'is_admin': is_admin
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    return {'token': token}, 200

@server.route('/validate', methods=['POST'])
def validate():
    token = request.headers.get('Authorization')
    if not token:
        return 'Token is missing', 401
    
    try:
        token = token.split(" ")[1]  # Remove 'Bearer ' prefix
        payload = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
        return payload, 200
    except jwt.ExpiredSignatureError:
        return 'Token has expired', 401
    except jwt.InvalidTokenError:
        return 'Invalid token', 401


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=5000)
