#!/usr/bin/python3
import mysql.connector
hostname="ip-10-0-1-243.ec2.internal"
mydb =mysql.connector.connect(host=hostname,user="admin", database="test")


mycursor = mydb.cursor()
from translate import Translator
import json
import boto3
from seqtolang import Detector

detector = Detector()
s3_client=boto3.client('s3')
S3_BUCKET = 'reviewsbct'
S3_PREFIX = 'sample_'


response = s3_client.list_objects_v2(Bucket=S3_BUCKET,Prefix=S3_PREFIX, StartAfter=S3_PREFIX,)
s3_files = response["Contents"]

for s3_file in s3_files:
    file_content = json.loads(s3_client.get_object(Bucket=S3_BUCKET, Key=s3_file["Key"])["Body"].read())
    _id=file_content["_id"]
    movie_name=file_content["movie_name"]
    release_year=file_content["release_year"]
    producer=file_content["producer"]
    director=file_content["director"]
    review_text =file_content["review_text"]
    user_name=file_content["user_name"]
    tokens = detector.detect(review_text)
    if tokens[0][0]=="deu":
        detected_lang= "German"
        translator= Translator(from_lang="German",to_lang="English")
    elif tokens[0][0]=="fr":
        detected_lang= "French"
        translator= Translator(from_lang="French",to_lang="English")

    score=float(tokens[0][1])
    sql = "INSERT INTO movies (_id, movie_name, release_year, producer,director,review ,user_name, detected_lang,score ) VALUES (%s, %s,%s ,%s, %s,%s,%s,%s, %s)"
    val=(_id, movie_name, release_year,producer,director,review_text ,user_name, detected_lang,score)
    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")
    print("_________________________________________")
