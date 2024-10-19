from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from facial_recognition import register_face, authenticate_face  # Assuming these are your utility functions

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Static Files - Make sure to put your frontend files in the 'frontend' directory

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")



# Serve index.html as the root file
@app.get("/")
async def read_index():
    return FileResponse(r'frontend\static\register.html')
# Serve register.html as a GET request

@app.get("/register.html")
async def read_register():
    try:
        # Assuming the file is in 'frontend/static'
        return FileResponse(r'frontend\static\register.html')
    except Exception as e:
        return JSONResponse(status_code=404, content={"message": str(e)})


# Registration endpoint
@app.post("/register")
async def register_user(first_name: str = Form(...), last_name: str = Form(...), image: UploadFile = File(...)):
    if not image.filename.endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    image_data = await image.read()
    success = register_face(image_data, first_name, last_name)

    if success:
        # Return success message and appropriate audio path
        return {"message": "User registered successfully", "audio": "/static/audio/Successfully registered f 1.wav"}
    else:
        # Return failure message and appropriate audio path
        raise HTTPException(status_code=500, detail="Registration failed", headers={"audio": "/static/audio/Registering new faces th 1.wav"})  # Proper error handling




# Authentication endpoint
@app.post("/authenticate")
async def authenticate_user(image: UploadFile = File(...)):
    if not image.filename.endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    image_data = await image.read()
    result = authenticate_face(image_data)

    if result and result["message"] == "Authentication successful":
        # Authentication successful
        return {"message": result["message"], "user": result["user"], "audio": result["audio"]}
    else:
        # Authentication failed
        return JSONResponse(
            status_code=401,  # Set status to 401 Unauthorized
            content={"message": result["message"], "audio": result["audio"]}
        )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001) 