#dependencies
import pandas as pd
import numpy as np

#Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func

from flask import Flask, render_template, jsonify

#Flask setup
app = Flask(__name__)
#create engine connection to sqlite database
engine = create_engine(
    "sqlite:///db/belly_button_biodiversity.sqlite", echo=False)

#reflect database into ORM class
Base = automap_base()
Base.prepare(engine, reflect=True)
#Base.classes.keys()

#create a session - link from Python to database
session = Session(engine)

#save references to table
Otu = Base.classes.otu
Samples = Base.classes.samples
Samples_metadata = Base.classes.samples_metadata

# create route that renders index.html template

@app.route("/")
def home():
   return render_template("index.html")


@app.route("/names")
def names():
   #create empty list
   sample_names = []

   results = session.query(Samples_metadata.SAMPLEID).all()

   #loop and append ids
   for result in results:
       sample_names.append("BB_" + str(result[0]))

   print("sample name")
   print(sample_names)
   return jsonify(sample_names)


@app.route("/otu")
def otu():
   results = session.query(Otu.lowest_taxonomic_unit_found).all()
   otu_list = list(np.ravel(results))

   #print("result")
   #print(results)
   return jsonify(otu_list)


@app.route("/metadata/<sample>")
def metadataSample(sample):
   #slice sample to only get number
   sample_number = int(sample[3:])
   metadata_results = session.query(Samples_metadata)\
       .filter(Samples_metadata.SAMPLEID == sample_number).all()

   data_list = []
   for metadata in metadata_results:
      # create dict for all queried objects
       sample_data = {
           "AGE": metadata.AGE,
           "BBTYPE": metadata.BBTYPE,
           "ETHNICITY": metadata.ETHNICITY,
           "GENDER": metadata.GENDER,
           "LOCATION": metadata.LOCATION,
           "SAMPLEID": metadata.SAMPLEID,
       }

       data_list.append(sample_data)

   for data in data_list:
       # only return metadata if sample id number matches queried id
       if data["SAMPLEID"] == sample_number:
           return jsonify(data)


@app.route("/wfreq/<sample>")
def wfreq(sample):
   #slice sample to only get number
   sample_number = int(sample[3:])
   wfreq_results = session.query(Samples_metadata.WFREQ)\
                   .filter(Samples_metadata.SAMPLEID == sample_number).all()
   wfreq = np.ravel(wfreq_results)

   #return only number value
   return jsonify(int(wfreq[0]))


@app.route("/samples/<sample>")
def samples(sample):
   sample_results = session.query(Samples).statement
   df = pd.read_sql_query(sample_results, session.bind)

   # return only values greater than 1
   df = df[df[sample] > 1]

   # sort values of samples by descending order
   df = df.sort_values(by=sample, ascending=False)

   # format data
   otu_sample_values = [{
       "otu_ids": df[sample].index.values.tolist(),
       "sample_values": df[sample].values.tolist()
   }]

   return jsonify(otu_sample_values)


if __name__ == "__main__":
   app.run(debug=True)
