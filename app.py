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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement
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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"-Replace start with (YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end<br/>"
        f"-Replace start/end with (YYYY-MM-DD)"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    query_date = dt.datetime(2017 , 8 ,23) - dt.timedelta(days=366)
    prec_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > query_date).\
        order_by(Measurement.date).all()

    prec_list = []
    for row in prec_data:
        temp_list = {}
        temp_list["date"] = row[0]
        temp_list["prcp"] = row[1]
        prec_list.append(temp_list)

    session.close()
    return jsonify(prec_list)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station():
    station_query = session.query(Station.name, Station.station).all()
    session.close()
    return jsonify(station_query)



# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    query_date = dt.datetime(2017 , 8 ,23) - dt.timedelta(days=366)
    #identifies most active station
    station_count = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
        order_by(func.count(Measurement.tobs).desc()).all()
    temp_df = session.query(Measurement.date, Measurement.tobs).\
        filter(func.strftime('%Y-%m-%d', Measurement.date) > query_date).\
        filter(Measurement.station == station_count[0][0]).all()
    
    prec_list = []
    for row in temp_df:
        temp_list = {}
        temp_list["date"] = row[0]
        temp_list["prcp"] = row[1]
        prec_list.append(temp_list)
    session.close()  
    return jsonify(prec_list)



# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measuremens.tobs)).\
        filter(Measurement.date >= start_date)



if __name__ == "__main__":
    app.run(debug=True)