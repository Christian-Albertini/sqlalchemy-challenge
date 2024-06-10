# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement=Base.classes.measurement
station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)

#################################################
# Flask Routes
#################################################
#Welcome page
@app.route("/")
def welcome():
    """List all available API routes."""
    return(
        f"Welcome to my Hawaii SQL API Webpage<br/>"
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperatures for last year: /api/v1.0/tobs<br/>"
        f"Temperatures starting at: /api/v1.0/<start(yyyy-mm-dd)><br/>"
        f"Temperatures from : /api/v1.0/<start(yyyy-mm-dd)>/<end(yyyy-mm-dd)><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """List all precipitation data"""
    #session=Session(engine)
    #Get latest day and calculate 1 year earlier from that
    latest=session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest=dt.datetime.strptime(latest[0], '%Y-%m-%d')
    one_year=dt.date(latest.year -1,latest.month, latest.day)
    #Query for dates and precipitation for one year
    data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year).\
        all()
    session.close()

    #create dict from list
    prcp_data=[]
    for date, prcp in data:
        prcp_dict={}
        prcp_dict['date']=date
        prcp_dict['prcp']=prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    """List all Stations"""
    #session=Session(engine)
    #Query for all stations
    data=session.query(station.station).order_by(station.station).all()

    session.close()

    #create dict from list
    station_data=[]
    for station in data:
        station_dict={}
        station_dict['station']=station
        station_data.append(station_dict)

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    """List temperatures from last year"""
    #session=Session(engine)
    #Get latest day and calculate 1 year earlier from that
    latest=session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest=dt.datetime.strptime(latest[0], '%Y-%m-%d')
    one_year=dt.date(latest.year -1,latest.month, latest.day)
    #Query for date and temperatures in the last year
    data=session.query(measurement.date, measurement.tobs).filter(measurement.date>=one_year).all()
    session.close()

    #create dict from list
    temp_data=[]
    for date, tobs in data:
        temp_dict={}
        temp_dict['date']=date
        temp_data['tobs']=tobs
        temp_data.append(temp_dict)

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def find_start(start_date):
    """Find temperatures starting at certain date"""
    #session=Session(engine)
    #Query to find the min, max and average temperature from start date onwards
    data=session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date>=start_date).all()
    session.close()

    #create dict from list
    tobs_data=[]
    for min, max, avg in data:
        tobs_dict={}
        tobs_dict['Minimum']=min
        tobs_data['Maximum']=max
        tobs_data['Average']=avg
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>/<end>")
def find_start_end(start_date, end_date):
    #Query to find the min, max, and average temperatures from one date to another
    """Find temperatures between two set dates"""
    #session=Session(engine)
    data=session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date>=start_date).filter(measurement.date<=end_date).all()
    session.close()

    #create dict from list
    tobs_data=[]
    for min, max, avg in data:
        tobs_dict={}
        tobs_dict['Minimum']=min
        tobs_data['Maximum']=max
        tobs_data['Average']=avg
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

#stop running webpage
if __name__ == '__main__':
    app.run(debug=True)