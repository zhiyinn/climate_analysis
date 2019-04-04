import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
import pandas as pd


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurements = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
       
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rainfall in prior year"""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()
    
    # create list of dicts with `date` and `prcp` as keys and values
    total_rain = []
    for x in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        total_rain.append(row)

    return jsonify(total_rain)


@app.route("/api/v1.0/stations")
def station():
    station_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(station_query.statement, station_query.session.bind)
    return jsonify(stations.to_dict())


@app.route("/api/v1.0/tobs")
def tobs():
    """Return list of temperature observations for prior year"""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()

# create list of dicts with `date` and `tobs` as keys and values
    temperature_total = []
    for result in temp:
        row = {}
        row["date"] = temp[0]
        row["tobs"] = temp[1]
        temperature_total.append(row)

    return jsonify(temperature_total)

@app.route('/api/v1.0/start/')
def given_date(date):
    """Return the average temp, max temp, and min temp for the date"""
    results = session.query(Measurements.date, func.avg(Measurements.tobs), func.max(Measurements.tobs), func.min(Measurements.tobs)).\
        filter(Measurements.date >= date).all()

#create dict
    data_list = []
    for result in results:
        row = {}
        row['Date'] = result[0]
        row['Average Temperature'] = float(result[1])
        row['Highest Temperature'] = float(result[2])
        row['Lowest Temperature'] = float(result[3])
        data_list.append(row)

    return jsonify(data_list)

@app.route("/api/v1.0/<start>/<end>")
def trip(start,end):

  # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)


if __name__ == '__main__':
    app.run(debug=True)
