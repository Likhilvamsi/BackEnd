"""from sqlalchemy import create_engine,text
username = "root"
password = "1234"
host = "localhost"
port = "3306"
db_name = "practice"
 
engine=create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}")

try :
    with engine.connect() as connection:
        res=connection.execute(text("SELECT * FROM USERS"))
        for r in res:
            print(r)
except Exception as e:
    print("database connection error :",e)"""


from fastapi import FastAPI
app=FastAPI()
@app.get("/")
def getdata():
    conection.execute(text("select * from users"))