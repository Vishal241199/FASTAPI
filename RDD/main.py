#Step-1- py -3 -m venv env1--------->to create a Virtual env
#Step-2- .\env1\Scripts\python.exe----->to activate python interpreter
#Step-3- env1\Scripts\activate.bat------>to activate the virtual env
#Step-4- pip install uvicorn[all]------->Uvicorn server installation



from random import randrange
from typing import Optional
from fastapi import Depends, FastAPI,Response,HTTPException,status
from fastapi.params import Body
from pydantic import BaseModel
from . import Filter
from datetime import datetime
from datetime import timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models



 
app = FastAPI()

#---------->To test if sqlalchemy is working correctly in DB<----------------------------



@app.get("/")
async def root():
    return {"message": "This is an HTTP get method"}

@app.get("/newpost")
def get_post():
    return{"getpost":"This is the new post"}

@app.post("/Createpost")
def create_post():
    return{"Postrequest":"Success"}

#If we send a details in body of the PM to create the the posts,
#we can retreive the data which is inside the body of the PM by,


@app.post("/Create_Post")
def Create_Post(Payload: dict = Body(...)):
    print(Payload)
    return {"message":"Post is created successfully"}

#from pydantic import basemodel---> this will tell the front end to restrict the userinput in a schema
#which can be expected.
class post(BaseModel):
    title:str
    content:str

@app.post("/New_post")
def New_post(a :post):
    print("title is", a.title)
    print("content is", a.content)
    return{"Data":"successful","response":"200ok"}

#----------> SASI REQUIREMENT [RDD] <------------------
@app.post("/Update_RDD_posts")
def Update_Rdd(a:Filter.Basic_structure):
    
    OL_Var=[]
    OL_length= len(a.Order.OrderLine)
    b=0
    for i in a.Order.OrderLine:
        Out={"OrderId":"","PK":"","OrderLine":OL_Var}
        if i["IsRefundGiftCard"]==True:
            Out["OrderId"]=i["OrderId"]
            Out["PK"]=str(a.Order.PK)
            c=i["CreatedTimestamp"]
            sliced_date=c[0:10]
            e=datetime.strptime(sliced_date, "%Y-%m-%d")
            f=e+timedelta(days=41)
            b=[{"RequestedDeliveryDate":f,"ItemId":i["ItemId"],
                "OrderLineId":i["OrderLineId"],"Extended":{"O4UPC":i["Extended"]["O4UPC"]}}]
            OL_Var.append(b)
        elif i["IsRefundGiftCard"]!=True:
            Out["OrderId"]=i["OrderId"]
            Out["PK"]=str(a.Order.PK)
            b+=1 
    if OL_length==b:
        Out.pop("OrderLine")            
    return(Out)

    


# -----------------> ITEMS_POST<------------------#
#creating a post based on pydantic model[schema validation]
class a_1(BaseModel):
    title:str
    topic:str
    Pno:int = None
    id:Optional[int]=None 
    rating:Optional[int]=None

Var_1=[{"title":"A","topic":"a","Pno":1,"id":1},{"title":"B","topic":"b","Pno":2,"id":2}]
@app.post("/post_1")
def post_1(A_1:a_1):
    print(A_1.dict())
    

    #if want to access a property,
    print(A_1.title)
    print(A_1.rating)
    return {"data":A_1}

#if we want to get the posted data

@app.get("/get_posts")
def get_post():
    return {"data":Var_1}

#If we want to add a post to Var_1 list
@app.post("/add",status_code=status.HTTP_201_CREATED)
def post_2(add_1:a_1):
    
    Converted_dict=add_1.dict()
    Converted_dict["id"]=randrange(1,1000000000)
    Var_1.append(Converted_dict)
    return{"data":Var_1}

#If we want to get one post.


@app.get("/onepost/{id}")
def one_post(id:int):
    for i in Var_1:
        if i["id"]==id:
            return {"title":i["title"],
                    "topic":i["topic"],
                    "Pno":i["Pno"],"id":i["id"]}
        


#IF we post is not found then we need to manipulate the response to 404
#from FastAPI import Response,HTTPException
        
@app.get("/onepost/{id}")
def one_post(id:int,response:Response):
    for i in Var_1:
        if i["id"]!=id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} is not found")
            #response.status_code=404
            #return {"title":i["title"],
              #      "topic":i["topic"],
              #      "Pno":i["Pno"],"id":i["id"]}



#-----------> Code for DB connection & extraction of data & adding the data<-------------
try:
    conn = psycopg2.connect(host='localhost',database='FastAPI',user='postgres',
    password='2025Vs@Torrid',cursor_factory=RealDictCursor)
    cursor= conn.cursor()
    print("DB connection is successfull")
except Exception as error:
    print("DB connection is failed")
    print("Error:",error)

@app.get("/get_posts_fromDB")
def get_post():
    cursor.execute("""SELECT * FROM posts""")
    p=cursor.fetchall()
    print(p)
    return {"data":p}

#--------->adding the data <----------------
class a_2(BaseModel):
    title:str
    topic:str
    Pno:Optional[int]=None
    id:Optional[int]=None 
    rating:Optional[int]=None

@app.post("/add_post_toDB",status_code=status.HTTP_201_CREATED)
def post_2(P_2:a_2):
    cursor.execute("""INSERT INTO posts (ID, title, topic) VALUES (%s, %s, %s) RETURNING * """,
                   (P_2.id, P_2.title, P_2.topic)) 
    Created_post = cursor.fetchone()
    conn.commit()
    return{"data":Created_post}


#-------->Fetching the data by ID<------------------

@app.get("/get_onepost_fromDB/{id}")
def get_one_post(id:str):
    cursor.execute("""SELECT * FROM posts WHERE id=%s""",(str(id),))
    one_post1=cursor.fetchone()
    if not one_post1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id} was not found")
    return {"post_detail":one_post1}

#------->DELETING POST BY ID<----------------------------
@app.delete("/delete_post/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    cursor.execute("""DELETE FROM posts WHERE id=%s returning *""",(str(id)))
    deleted_post= cursor.fetchone()
    conn.commit()
    if deleted_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id}does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#------->UPDATE[Put] POST BY ID <-----------
@app.put("/Put_posts/{id}")
def update_post_inDB(id:int,input_var:a_2):
    cursor.execute("""UPDATE posts SET title=%s, topic=%s, rating=%s WHERE id =%s RETURNING*""",
                   (input_var.title,input_var.topic,input_var.rating,str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id}does not exist")
    return {"data":updated_post}




    





