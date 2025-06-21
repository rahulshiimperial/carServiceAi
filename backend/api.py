from livekit.agents import llm
import enum
from typing import Annotated
import logging
from db_driver import MongoDatabaseDriver  # <-- updated driver class

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = MongoDatabaseDriver()  

class CarDetails(enum.Enum):
    VIN = "vin"
    Make = "make"
    Model = "model"
    Year = "year"

class AssisstantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        
        self._car_details = {
            CarDetails.VIN.value: "",
            CarDetails.Make.value: "",
            CarDetails.Model.value: "",
            CarDetails.Year.value: ""
        }
    
    def get_car_str(self):
        return "\n".join(f"{key.capitalize()}: {value}" for key, value in self._car_details.items())
    
    @llm.ai_callable(description="Lookup a car by its VIN")
    def lookup_car(self, vin: Annotated[str, llm.TypeInfo(description="The VIN of the car to lookup")]):
        logger.info("Lookup car - VIN: %s", vin)
        
        result = DB.get_car_by_vin(vin)
        if result is None:
            return "Car not found"
        
        self._car_details = {
            CarDetails.VIN.value: result.vin,
            CarDetails.Make.value: result.make,
            CarDetails.Model.value: result.model,
            CarDetails.Year.value: result.year
        }
        
        return f"The car details are:\n{self.get_car_str()}"
    
    @llm.ai_callable(description="Get the details of the current car")
    def get_car_details(self):
        logger.info("Get car details")
        return f"The car details are:\n{self.get_car_str()}"
    
    @llm.ai_callable(description="Create a new car")
    def create_car(
        self, 
        vin: Annotated[str, llm.TypeInfo(description="The VIN of the car")],
        make: Annotated[str, llm.TypeInfo(description="The make of the car")],
        model: Annotated[str, llm.TypeInfo(description="The model of the car")],
        year: Annotated[int, llm.TypeInfo(description="The year of the car")]
    ):
        logger.info("Create car - VIN: %s, Make: %s, Model: %s, Year: %s", vin, make, model, year)
        result = DB.create_car(vin, make, model, year)
        if result is None:
            return "Failed to create car. Possibly duplicate VIN."
        
        self._car_details = {
            CarDetails.VIN.value: result.vin,
            CarDetails.Make.value: result.make,
            CarDetails.Model.value: result.model,
            CarDetails.Year.value: result.year
        }
        
        return "Car created!"
    
    def has_car(self):
        return self._car_details[CarDetails.VIN.value] != ""
