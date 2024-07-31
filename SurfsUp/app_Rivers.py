# Import the dependencies. I imported some I may not have used on this assignment, but I kept them on just in case.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text, inspect, select, MetaData, Table

import pandas as pd
import datetime as dt
import numpy as np

from flask import Flask, jsonify, render_template, request


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    # I used this template because we learned about the index file in class, and I thought I'd try it out on this assignment.
    return  render_template("index.html")

@app.route("/api/v1.0/routes")
def routes_handler():
    return (
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature Observations: /api/v1.0/tobs<br/>"
        f"Start Date (mmddYYYY): /api/v1.insert_start_date<br/>"
        f"Start and End Date (mmddYYYY/mmddYYYY): /api/v1.insert_start_date/end_date<br/>"
    )

# I received help from my tutor, Anna Poulakos on this route
@app.route("/api/v1.0/precipitation")
def precipitation_handler():
    # Using my code from my Jupyter Notebook
    # Calculate the date one year from the last date in data set.
    one_year_back = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_back).all()

    # Convert the results to a dictionary
    result = {date:prcp for date,prcp in scores}

    # close the session
    session.close()
    
    # what returns
    return jsonify(result)

# I asked Xpert how to display the results from my query in a list to help me with this one.
@app.route("/api/v1.0/stations")
def stations_handler():
    # Perform a query to get the stations
    stations = session.query(Station.station).all()
    # Get the station names from the query in a list
    station_list = [station for (station,) in stations]

    session.close()

    return jsonify(station_list)

# Using my code from the Jupyter notebook and what I learned from the Precipitation route
@app.route("/api/v1.0/tobs")
def tobs_handler():
    # Calculate the date one year from the last date in the most-active station.
    one_year_back2 = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and tobs
    tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281', Measurement.date >= one_year_back2).all()

    # Convert the results to a dictionary
    results2 = {date:tobs for date,tobs in tobs}

    session.close()

    return jsonify(results2)

# I utilized a combination of Xpert and Alexander's code on this one.
@app.route("/api/v1.0/<start>")
def start_handler(start=None):
    # Statement for the measurments needed
    min_avg_max = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    start = dt.datetime.strptime(start, "%m%d%Y")
    results = session.query(*min_avg_max).\
        filter(Measurement.date >= start).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temperatures=temps)


@app.route("/api/v1.0/<start>/<end>")
def start_end_handler(start=None, end=None):
    # # Statement for the measurments needed
    min_avg_max = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # calculate TMIN, TAVG, TMAX with start and end
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*min_avg_max).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temperatures=temps)




if __name__ == "__main__":
    app.run(debug=True)
