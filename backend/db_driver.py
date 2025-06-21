from dataclasses import dataclass, asdict
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


@dataclass
class Car:
    vin: str
    make: str
    model: str
    year: int


class MongoDatabaseDriver:
    def __init__(self, db_name="auto_db", collection_name="cars", uri="mongodb+srv://rairahulmrt:1am%40Rahul.rai@cluster0.ieuu6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # Ensure VIN is unique (like PRIMARY KEY)
        self.collection.create_index("vin", unique=True)

    def create_car(self, vin: str, make: str, model: str, year: int) -> Optional[Car]:
        car = Car(vin=vin, make=make, model=model, year=year)
        try:
            self.collection.insert_one(asdict(car))
            return car
        except DuplicateKeyError:
            print(f"Car with VIN {vin} already exists.")
            return None

    def get_car_by_vin(self, vin: str) -> Optional[Car]:
        result = self.collection.find_one({"vin": vin})
        if result:
            return Car(
                vin=result["vin"],
                make=result["make"],
                model=result["model"],
                year=result["year"]
            )
        return None
