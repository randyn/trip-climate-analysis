from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement

def getLastYearDate(session):
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], "%Y-%m-%d")
    last_year_date = last_date.replace(year=last_date.year - 1)
    return last_year_date

def calc_temps(session, start_date, end_date=None):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date)
    query = query if end_date is None else query.filter(Measurement.date <= end_date)
    return query.all()

@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate Analysis API<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    last_year_date = getLastYearDate(session)
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
        .filter(func.date(Measurement.date) > last_year_date - dt.timedelta(days=1))\
        .order_by(Measurement.date)\
        .all()
    session.close()
    precipitation_dict = {date: precipitation for date, precipitation in precipitation_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(Station.station).all()
    session.close()
    station_list = list(np.ravel(station_data))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temperatureObservations():
    session = Session(engine)
    last_year_date = getLastYearDate(session)
    temperature_data = session.query(Measurement.tobs)\
        .filter(Measurement.station == 'USC00519281', Measurement.date > last_year_date - dt.timedelta(days=1))\
        .all()
    session.close()
    temperature_list = list(np.ravel(temperature_data))
    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp(start, end=None):
    session = Session(engine)
    temps = calc_temps(session, start, end)
    session.close()
    temps = list(np.ravel(temps))
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
