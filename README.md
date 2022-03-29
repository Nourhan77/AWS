Install from source:# Solution Diagram
![Solution Diagram](https://user-images.githubusercontent.com/60991241/160599286-cabc4fdc-9782-48fd-8001-abaceacd6237.png)

We will use On Demand Instance to reduce cost as we don't sure how many times we will use the application,
the number of times we will use it depends on reviews collected from users which is not constant.
Also, we need to use Infrequent Access S3.

# Scaling
We can create our own custom strategy, per the metrics and thresholds we define for scaling. 
We can set separate strategies for each resource or resource type.

The following scaling strategies are available:

1-Optimize for availability—AWS: Auto Scaling scales the resource out and in automatically to maintain resource utilization at 40 percent. This option is useful when your application has urgent and sometimes unpredictable scaling needs.

2-Balance availability and cost—AWS: Auto Scaling scales the resource out and in automatically to maintain resource utilization at 50 percent. This option helps you maintain high availability while also reducing costs.

3-Optimize for cost—AWS: Auto Scaling scales the resource out and in automatically to maintain resource utilization at 70 percent. This option is useful for lowering costs if your application can handle having reduced buffer capacity when there are unexpected changes in demand.


# Getting Started 
Install from source:
```
$ git clone https://github.com/Nourhan77/Challenge1
$ docker build --tag challenge1 .
$ docker-compose up -d
$ docker container run challenge1
```
Giving Privileges on our database to 'admin' user and host ip
```
GRANT ALL PRIVILEGES ON * . * TO 'admin'@'ip-10-0-1-243.ec2.internal';
FLUSH PRIVILEGES;
```

# Code Runs
Taking files from s3 bucket 
then doing our pipeline to store data in database

```
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

‘’’ Read files from s3  here bucket’s name is 'reviewsbct' and prefix of files is sample _
(ex. sample_0, sample_1,….).’’’
s3_client=boto3.client('s3')
S3_BUCKET = 'reviewsbct'
S3_PREFIX = 'sample_ '
response = s3_client.list_objects_v2(Bucket=S3_BUCKET,Prefix=S3_PREFIX, StartAfter=S3_PREFIX,)



#parsing all json keys in each file in variables that we then parse them as values records in the table movies of test database 
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
#Detecting language and translate to english
    if tokens[0][0]=="deu":
        detected_lang= "German"
        translator= Translator(from_lang="German",to_lang="English")
    elif tokens[0][0]=="fr":
        detected_lang= "French"
        translator= Translator(from_lang="French",to_lang="English")
#get the score of sentiment analysis
    score=float(tokens[0][1])

# Insert variables as values records in the table movies of test database 
    sql = "INSERT INTO movies (_id, movie_name, release_year, producer,director,review ,user_name, detected_lang,score ) VALUES (%s, %s,%s ,%s, %s,%s,%s,%s, %s)"
    val=(_id, movie_name, release_year,producer,director,review_text ,user_name, detected_lang,score)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")
    print("_________________________________________")

```
Passing Environment Variables used by MySQL container in ```file.env```

```
ports="3308:3306"
DATABASE_HOST="host.docker.internal"
DATABASE_USERNAME="root"
```


# Decompose file

```
version: "3.0"

services:
  mysqldb:
    env_file:
      - file.env
    image: mysql
    hostname: mysql
    container_name: mysql
    restart: always
    environment:
      USER: "admin"
      MYSQL_ROOT_PASSWORD: "invalid"
      MYSQL_DATABASE: "test"
      MYSQL_HOST: "host.docker.internal"
    volumes:
      - mysql:/var/lib/mysql
      - mysql_config:/etc/mysql
volumes:
  mysql:
  mysql_config:    
```
