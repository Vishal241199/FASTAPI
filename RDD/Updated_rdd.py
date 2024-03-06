from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from . import Filter

app=FastAPI()

@app.post("/RDD_New")
def update_rdd(p:Filter.Basic_structure):
    Out={"OrderId":"","PK":"","OrderLine":""}
    for i in p.Order.OrderLine:
        if i["IsGiftCard"]==1 and i["IsRefundGiftCard"]==1:
            Out["OrderId"]=i["OrderId"]
            print(Out["OrderId"])
            