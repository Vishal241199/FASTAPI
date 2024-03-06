
from typing import Optional
from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel

class orderdata(BaseModel):
    OrderLine:list
    PK:int

class configdata(BaseModel):
    Add_RDD_Days:int
    GC_Threshold:int

class Basic_structure(BaseModel):
    Messages:Optional[int]=None
    Order:orderdata
    ConfigStoreMap:configdata















    