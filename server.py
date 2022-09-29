from flask import Flask, redirect, url_for, request, make_response
from flask_cors import CORS, cross_origin
import json
import csv
import fileinput
from tempfile import NamedTemporaryFile
import shutil

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def index():
    return "<img src='https://c.tenor.com/CJ0dfPteO0MAAAAd/why-do.gif'/>"

def return_error():
    response = make_response("Something went wrong lol")
    response.status_code = 500
    return response

fields=["steamid","kills","deaths","highest_killstreak"]

filename = 'users.csv'
tempfile = NamedTemporaryFile(mode='w', delete=False)

@app.route("/get_info", methods=["GET"])
@cross_origin()
def get_info():
    try:
        with open("users.csv", "r") as users_file:
            data = users_file.readlines()
        response = make_response(data)
        response.status_code = 200
        return response
    except:
        return return_error()

@app.route("/submit_info", methods=["GET", "POST"])
@cross_origin()
def submit_info():
    if request.method != "POST":
        response = make_response("Invalid request")
        response.status_code = 400
        return response
    
    try:
        request_data = str(request.get_data().decode())
        request_json = json.loads(request_data)
        keys = request_json.keys()
        contains_key = lambda key : key in keys

        if not(contains_key("steamid") and \
            contains_key("kills") and \
            contains_key("deaths") and \
            contains_key("highest_killstreak")):
            return return_error()

        steamid = request_json["steamid"]
        kills = request_json["kills"]
        deaths = request_json["deaths"]
        highest_killstreak = request_json["highest_killstreak"]

        if  type(steamid) != str or \
            type(kills) != int or \
            type(deaths) != int or \
            type(highest_killstreak) != int:
            return return_error()

        to_write = f"{steamid},{kills},{deaths},{highest_killstreak}\n"

        with open(r"users.csv") as users_file:
            reader = csv.reader(users_file)
            skip = True
            user_exists = False
            user_row = None

            for row in reader:
                if skip:
                    skip = False
                    continue

                if row[0] == steamid:
                    user_exists = True
                    user_row = row
                    break
        
        if user_exists:
            user_kills = int(row[1]) + kills
            user_deaths = int(row[2])+ deaths
            user_ks = int(row[3])

            if highest_killstreak > user_ks:
                user_ks = highest_killstreak

            to_write = f"{steamid},{user_kills},{user_deaths},{user_ks}\n"

            with open("users.csv", "r") as users_file:
                data = users_file.readlines()

            for i in range(0, len(data)):
                if data[i][0:len(steamid)] == steamid:
                    data[i] = to_write
                
            with open("users.csv", "w") as users_file:
                users_file.writelines(data)
        else:
            with open("users.csv", "a") as users_file:
                users_file.writelines(to_write)
            
        response = make_response(f"Steam ID: {steamid} | Kills: {kills}\nDeaths: {deaths} | Highest killstreak: {highest_killstreak}\nBecomes -> {to_write}")
        response.status_code = 200
        return response
    except:
       return return_error()
