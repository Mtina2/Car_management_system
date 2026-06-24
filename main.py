import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status,Depends
from pydantic import BaseModel
from typing import Optional,Generator
from sqlmodel import SQLModel,Field, create_engine,Session,select
from contextlib import asynccontextmanager

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
      raise RuntimeError("DATABASE_URL environment variable not set")
engine=create_engine(DATABASE_URL)


app = FastAPI()

# (Models)
class Car(SQLModel, table=True):
    id: Optional[int] =Field(default=None, primary_key=True)
    brand: str
    model: str
    year: int
    price: float
    currency:str = "frs"
   


class CarResponse(BaseModel):
    id:int
    brand:str
    model:str
    year:int
    price:str

class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str]= None
    year: Optional[int] = None
    price: Optional[float] = None
    currency:Optional[str]= None


# DATABASE_URL ="sqlite:///cars.db"
# engine = create_engine(DATABASE_URL, connect_args= {"check_same_thread":False})

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_table()
    yield

app = FastAPI(lifespan=lifespan)

def get_session() -> Generator[Session,None,None]:
    with Session(engine)as session: 
        yield session


# CRUD Endpoints 

# GET ALL
@app.get("/cars", response_model=list[CarResponse])
def get_all_cars(session:Session=Depends(get_session)):
    cars=session.exec(select(Car)).all()
    return [
        CarResponse(
            id =car.id,
            brand=car.brand,
            model=car.model,
            year=car.year,
            price=f"{car.currency} {car.price}" ,
        )
        for car in cars
            ]

# GET ONE
@app.get("/cars/{car_id}", response_model=CarResponse)
def get_car(car_id: int,session:Session=Depends(get_session)):
    car =session.get(Car,car_id)
    if not car:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")
    return  CarResponse(
        id =car.id,
            brand=car.brand,
            model=car.model,
            year=car.year,
            price=f"{car.currency} {car.price}" ,
        )

    
# POST (Create)
@app.post("/cars", response_model=Car, status_code=201)
def create_car(car_in: Car, session:Session=Depends(get_session)):
    db_car = Car.model_validate(car_in)
    session.add(db_car)
    session.commit()
    session.refresh(db_car)
    return db_car

    
# PUT (Update)
@app.put("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, car_in: CarUpdate, session:Session=Depends (get_session)):
    db_car =session.get(Car,car_id)
    if not db_car:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")
    
    update_data = car_in.model_dump(exclude_unset=True)
    db_car.sqlmodel_update(update_data)
    
    session.add(db_car)
    session.commit()
    session.refresh(db_car)
    return db_car

# DELETE
@app.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int, session:Session=Depends (get_session)):
    db_car = session.get(Car,car_id)
    if not db_car:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")
    session.delete(db_car)
    session.commit()
    return None
    