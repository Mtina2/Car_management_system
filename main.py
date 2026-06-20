from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# --- 1. Schemas (Models) ---
class Car(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    price: float

class CarUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    price: float | None = None


# --- 2. In-Memory Database ---
# Storing full 'Car' objects so `.model_copy()` works instantly!
cars_db: dict[int, Car] = {
    1: Car(id=1, brand="Toyota", model="Corolla", year=2022, price=24000.0)
}
next_id = 2


# --- 3. CRUD Endpoints ---

# GET ALL
@app.get("/cars", response_model=list[Car])
def get_all_cars():
    return list(cars_db.values())

# GET ONE
@app.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int):
    if car_id not in cars_db:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")
    return cars_db[car_id]

# POST (Create)
@app.post("/cars", response_model=Car, status_code=201)
def create_car(car_in: CarUpdate):
    global next_id
    new_car = Car(
        id=next_id,
        brand=car_in.brand or "Unknown",
        model=car_in.model or "Unknown",
        year=car_in.year or 2000,
        price=car_in.price or 0.0
    )
    cars_db[next_id] = new_car
    next_id += 1
    return new_car

# PUT (Update)
@app.put("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, car_in: CarUpdate):
    if car_id not in cars_db:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")
    
    existing_car = cars_db[car_id]
    update_data = car_in.model_dump(exclude_unset=True)
    
    # Clean lecture note style update
    updated_car = existing_car.model_copy(update=update_data)
    cars_db[car_id] = updated_car
    return updated_car

# DELETE
@app.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int):
    if car_id not in cars_db:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")
    
    del cars_db[car_id]