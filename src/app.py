#!/usr/bin/env python3
import os
import requests
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


"""
Copyright (c) [2023] [Xinyue Lu]

In order to run this program to collect data and store into database,
please unzip the file, open terminal in mac, cd to the directory, 
and then run the 2 export commands below

(base) xinyuelu@Xinyues-MacBook-Pro flask_data_collection % export FLASK_APP=app
(base) xinyuelu@Xinyues-MacBook-Pro flask_data_collection % export FLASK_ENV=development


make sure flask is installed, and then you can run the command "flask run"
(base) xinyuelu@Xinyues-MacBook-Pro flask_data_collection % flask run

After "flask run", there will be 3 endpoints available:
main endpoint: http://127.0.0.1:5000, which will do data collection, storage and query all together
collection endpoint: http://127.0.0.1:5000/collectData, which will do data collection and storage
query endpoint: http://127.0.0.1:5000/queryData, which will do read-only query


"""

# this is the url endpoint which this service will monitor against
URL_DATA_SOURCE = "https://xinyuelu-mvp-website-23eeea900853.herokuapp.com"
DATA_FOLDER = "data"

app = Flask(__name__)

app_file_dir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.join(app_file_dir, "..")
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, DATA_FOLDER, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# here we initialize DB object, and connect DB with Flask application
db = SQLAlchemy(app)

"""
DB schema definition
"""
class HealthCheck(db.Model):
    datetime = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow())
    status_code = db.Column(db.Integer, nullable=False)
    endpoint = db.Column(db.String, nullable=False)

# create HealthCheck table
with app.app_context():
    db.create_all()

'''
Helper function to get status code from external source using API
'''
def get_status(url):
    response = requests.get(url)
    return response.status_code

def query_all_records():
    return HealthCheck.query.all()

def query_latest_record():
    return HealthCheck.query.order_by(HealthCheck.datetime.desc()).first()

"""
The main page behavior
It first collects and stores data into DB, and then returns data query from DB
"""
@app.route('/')
def main_page():
    collect()
    return query()

"""
The API for collecting data from external source, and store into database
"""
@app.route('/collectData')
def collect():
    status = get_status(URL_DATA_SOURCE)
    current_time = datetime.utcnow()
    new_entry = HealthCheck(datetime=current_time, status_code=status, endpoint=URL_DATA_SOURCE)
    db.session.add(new_entry)
    db.session.commit()
    return render_template('data_collection.html', 
                           datetime=current_time, 
                           status_code=status, 
                           endpoint=URL_DATA_SOURCE)


"""
The API for querying already-collected data from database.
This operation will be read-only
"""
@app.route('/queryData')
def query():
    records = query_all_records()
    latest_record = query_latest_record()
    return render_template('index.html', records=records, latest_record=latest_record)


if __name__ == "__main__":
    main_page()

