from flask import Flask, request, jsonify
from mysql.connector import errorcode
from werkzeug.exceptions import abort
import requests
import mysql.connector
import configparser
import logging
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(f'{dir_path}/flask_db.cfg')
logging.basicConfig(filename=config['LOG']['log_file'], level=config['LOG']['log_level'])


#Connection to DB
def connectionToDB():
    return mysql.connector.connect(
        user=config['DB']['mysql_user'],
        password=config['DB']['mysql_password'],
        host=config['DB']['mysql_host'],
        database=config['DB']['mysql_db'],
        auth_plugin='mysql_native_password')  

app = Flask(__name__)

# Select * From <TABLE>
@app.route('/select')
def select():
    if request.method == 'GET':
        try:
            mysqldb = connectionToDB()
            cursor =  mysqldb.cursor(buffered=True)
            query = f"SELECT * FROM {config['DB']['mysql_db']}.{config['DB']['mysql_table']};"
            cursor.execute(query)
            response = cursor.fetchall()
            mysqldb.close()
        except mysql.connector.Error as e:
            if(e.errno == errorcode.ER_ACCESS_DENIED_ERROR):
                logging.error(str(e))
                return("AUTH ERROR! PLEASE CHECK LOG FILE.")
            elif(e.errno == errorcode.ER_BAD_DB_ERROR):
                logging.error(str(e))
                return("DB NOT EXIST! PLEASE CHECK LOG FILE.")
            else:
                logging.error(str(e))
                return("SOME ERROR OCCURED! PLEASE CHECK LOG FILE.")         
    else:
        return make_response(jsonify(Error='The method you are trying to use is not supported, please use the GET method to insert data.'),405)
    return jsonify(response)

# Insert Query - http://0.0.0.0:8080/insert
@app.route('/insert', methods=['POST'])
def insert_query():
    if request.method == 'POST':
        json_obj = request.get_json(force=True)
        try:
            mysqldb = connectionToDB()
            cursor =  mysqldb.cursor(buffered=True)
            query = f"""INSERT INTO 
            abdullah.user (name, surname, mail) VALUES
            ('{(json_obj["name"])}', '{(json_obj["surname"])}', '{(json_obj["mail"])}');"""
            cursor.execute(query)
            mysqldb.commit()
            mysqldb.close()
        except mysql.connector.Error as e:
            if(e.errno == errorcode.ER_ACCESS_DENIED_ERROR):
                logging.error(str(e))
                return("AUTH ERROR! PLEASE CHECK LOG FILE.")
            
            elif(e.errno == errorcode.ER_BAD_DB_ERROR):
                logging.error(str(e))
                return("DB NOT EXIST! PLEASE CHECK LOG FILE.")

            else:
                logging.error(str(e))
                return("SOME ERROR OCCURED! PLEASE CHECK LOG FILE.")
    else:
        return make_response(jsonify(Error='The method you are trying to use is not supported, please use the POST method to insert data.'),405)     
    return("Your Data Successfully Inserted.")

@app.route('/delete', methods=['DELETE'])
def delete():
    mail = request.args.get("mail")
    if request.method == 'DELETE':
        try:
            mysqldb = connectionToDB()
            cursor =  mysqldb.cursor(buffered=True)
            query = f"""DELETE FROM {config['DB']['mysql_db']}.{config['DB']['mysql_table']} WHERE mail = '{mail}';"""
            cursor.execute(query)
            mysqldb.commit()
            mysqldb.close()
        except mysql.connector.Error as e:
            if(e.errno == errorcode.ER_ACCESS_DENIED_ERROR):
                logging.error(str(e))
                return("AUTH ERROR! PLEASE CHECK LOG FILE.")
            elif(e.errno == errorcode.ER_BAD_DB_ERROR):
                logging.error(str(e))
                return("DB NOT EXIST! PLEASE CHECK LOG FILE.")
            else:
                logging.error(str(e))
                return("SOME ERROR OCCURED! PLEASE CHECK LOG FILE.")         
    else:
        return make_response(jsonify(Error='The method you are trying to use is not supported, please use the DELETE method to insert data.'),405)
    return("Your Data Successfully DELETED.")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='8080')
