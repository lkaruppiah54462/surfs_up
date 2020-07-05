import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask,jsonify
#if check same thread not there, second querry fails
engine = create_engine("sqlite:///hawaii.sqlite",connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

#FLASK APPLICATION
#Define routes

app = Flask(__name__)

@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    /api/v1.0/temp/June
    /api/v1.0/temp/December
    ''')

@app.route("/api/v1.0/precipitation")
def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    seltemp = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    selprecp = [func.min(Measurement.prcp), func.avg(Measurement.prcp), func.max(Measurement.prcp)]
    if not end:
        resulttemp = session.query(*seltemp).filter(Measurement.station != 'USC00518838' and Measurement.station != 'USC00517948' ).filter(Measurement.date <= start).all()
        resultprecp = session.query(*selprecp).filter(Measurement.station != 'USC00518838' and Measurement.station != 'USC00517948').filter(Measurement.date <= start).all() 
        temps = list(np.ravel(resulttemp))
        precp = list(np.ravel(resultprecp))
        return jsonify(temps=temps,precp=precp)    
    resulttemp = session.query(*seltemp).filter(Measurement.station != 'USC00518838' and Measurement.station != 'USC00517948').filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    resultprecp = session.query(*selprecp).filter(Measurement.station != 'USC00518838' and Measurement.station != 'USC00517948').filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps = list(np.ravel(resulttemp))
    precp = list(np.ravel(resultprecp))
    return jsonify(temps=temps,precp=precp)

@app.route("/api/v1.0/temp/June")
def june():
    results = []
    m=6 #June
    results = session.query(Measurement.date, Measurement.prcp,Measurement.tobs).all()
    # Save the query results as a Pandas DataFrame and set the index to the date column
    df = pd.DataFrame(results, columns=['date','precipitation','temperature'])
    df['date'] = pd.to_datetime(df['date'])
    #print(df.head())
    df1 = df.loc[(df['date'].dt.month==m)]
    
    return jsonify(df1.describe().to_json())

@app.route("/api/v1.0/temp/December")
def december():
    results = []
    m=12 #June
    results = session.query(Measurement.date, Measurement.prcp,Measurement.tobs).all()
    # Save the query results as a Pandas DataFrame and set the index to the date column
    df = pd.DataFrame(results, columns=['date','precipitation','temperature'])
    df['date'] = pd.to_datetime(df['date'])
    #print(df.head())
    df1 = df.loc[(df['date'].dt.month==m)]
    
    return jsonify(df1.describe().to_json())
 
 
