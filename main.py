from fastapi import FastAPI
from project import om
from project import logger

logger.info("初始化:实例化FastApi中")
app = FastAPI()
logger.info("初始化:实例化FastApi完成")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
