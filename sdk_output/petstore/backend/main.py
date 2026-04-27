from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import schemas
from typing import List, Optional, Any

app = FastAPI(title="Swagger Petstore", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/pets", response_model=schemas.Pets)
async def listPets(limit: int = None):
    # Mock implementation for GET /pets
    return schemas.Pets()

@app.post("/pets", response_model=Any)
async def createPets(body: schemas.Pet):
    # Mock implementation for POST /pets
    return {"status": "success", "message": "Resource created/updated"}

@app.get("/pets/{petId}", response_model=schemas.Pet)
async def showPetById(petId: str):
    # Mock implementation for GET /pets/{petId}
    return schemas.Pet()

