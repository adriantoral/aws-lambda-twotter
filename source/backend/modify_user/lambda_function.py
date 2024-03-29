import json
from datetime import datetime

import jwt
import pymysql

SECRET = "PROYECTO3SISDIS2024"
# Encode token: jwt.encode({"some": "payload"}, "secret", algorithm="HS256")
# Decode token: jwt.decode(encoded, "secret", algorithms=["HS256"])

rds_host = "52.204.152.143"
username = "practica3"
password = "practica3"
database = "practica3"
bucketUrl = "https://0sc4r24sisdis2024.s3.us-east-1.amazonaws.com/"


def lambda_handler(event, context):
    # if "isBase64Encoded" in event:
    #     isEncoded = bool(event["isBase64Encoded"])
    #
    #     if isEncoded:
    #         decodedBytes = base64.b64decode(event["body"])
    #         decodedStr = decodedBytes.decode("ascii")
    #         print(json.dumps(parse_qs(decodedStr)))
    #         decodedEvent = json.loads(json.dumps(parse_qs(decodedStr)))
    #         user = decodedEvent["user"][0]
    #
    # else:
    #     user = event["body"]["user"]

    print(event)

    body = json.loads(event.get("body", "{}"))
    if "token" not in body:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': "Missing token"
        }

    user_id = None
    try:
        decoded = jwt.decode(body.get("token"), SECRET, algorithms=["HS256"])
        user_id = decoded.get('id')
        exp = decoded.get('exp')

        if datetime.now().timestamp() > exp:
            return {
                'statusCode': 401,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': "Token has expired"
            }

    except:
        return {
            'statusCode': 401,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': "Invalid token"
        }

    # Parametros del usuario
    rg_email = body.get('email', 'None')
    rg_avatar = body.get('avatar', 'https://cdn-icons-png.flaticon.com/512/9205/9205233.png')
    rg_biography = body.get('biography', 'None')

    conn = pymysql.connect(rds_host, user=username, passwd=password, db=database, connect_timeout=5)
    cursor = conn.cursor()

    error_value = {
        'statusCode': 400,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': "Username or email already exists"
    }

    # Suponemos que cursor execute verifica el SQL Injection (revisarlo en futuro)
    try:
        if cursor.execute("UPDATE users SET email = %s, avatar = %s, biography = %s WHERE id = %s", (rg_email, rg_avatar, rg_biography, user_id)):
            error_value = None
            conn.commit()
    except: pass

    cursor.close()
    conn.close()

    if error_value: return error_value

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': 'Updated'
    }
