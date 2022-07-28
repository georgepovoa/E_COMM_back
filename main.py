from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel, Field
import uuid
from typing import Union
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class User(BaseModel):
    _id:Union[str, None] = None
    nome:str
    email:str

class Produto(BaseModel):
    _id:Union[str, None] = None
    title:str
    sub_title:str
    description:str
    price:float
    image:str

    class Config:
        schema_extra = {
            "example": {
                "title": "IMPRESSORA",
                "sub_title": "LG 13246532",
                'description':'me sobra preguiça para descrever',
                "price": 300,
                "image":"https://picsum.photos/800/?random=123" ,
            }
        }


class Carrinho(BaseModel):
    _id:Union[str, None] = None
    user:str
    produtos:list

CONNECTION_STRING = "mongodb+srv://admin:admin@cluster0.bqvnz.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)
db = client['eshop']
products_col = db["products_col"] 
carrinho_col = db["carrinho_col"] 


@app.get("/")
async def root():

    
    return {"message": "Hello World"}

@app.post('/produtos')
async def insert_product(produto:Produto):
    produto = produto.__dict__
    produto["_id"] = str(uuid.uuid4())
    products_col.insert_one(produto)
    
    return produto 

@app.get('/produtos/all')
def get_product():
    products_find = products_col.find()
    return list(products_col.find())

@app.get('/carrinhos/{user}')
async def get_carrinho_user(user:str):
    carrinho_list = carrinho_col.find_one({"user":user})
    produto_list = list(products_col.find({"_id":{"$in":carrinho_list['produtos']}}))
    carrinho_list["produtos_abertos"] = produto_list
    return carrinho_list

@app.get('/carrinhos')
async def get_carrinho():
    carrinho_list = carrinho_col.find_one()
    produto_list = list(products_col.find({"_id":{"$in":carrinho_list['produtos']}}))
    carrinho_list["produtos_abertos"] = produto_list
    return carrinho_list

@app.post("/carrinhos")
async def post_carrinho(carrinho:Carrinho):
    
    carrinho = carrinho.__dict__
    carrinho["_id"] = str(uuid.uuid4())
    carrinho_col.insert_one(carrinho)

@app.put("/carrinhos/add/{user}/{id}")
async def add_to_carrinho(user:str,id:str):
    carrinho_col.update_one({'user':user},{'$push':{'produtos':id}},upsert=True)
    return {"OK":"OK"}

@app.put("/carrinhos/remove/{user}/{id}")
async def add_to_carrinho(user:str,id:str):
    carrinho_col.update_one({'user':user},{'$pull':{'produtos':id}},upsert=True)
    return {"OK":"OK"}





    





