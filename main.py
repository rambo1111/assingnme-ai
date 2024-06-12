from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# import google.generativeai as genai
import tempfile
# import fitz  # PyMuPDF
# from PIL import Image
import os
# from google.generativeai.types import HarmCategory, HarmBlockThreshold
# import requests
from process import handle_file

app = FastAPI()

# Configure CORS to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
# def continuous_requests():
#     try:
#         response = requests.get("https://test-assingnement-api.onrender.com/keep-alive")
#         print(response.text)
#     except Exception as e:
#         print(f"Error occurred: {e}")
#     time.sleep(10)

# def restart_server():
#     logger.info("Server is restarting...")
#     try:
#         # Command to run
#         cmd_command = "uvicorn main:app --reload"
#         response = requests.get("https://test-assingnement-api.onrender.com/keep-alive")

#         # Run the command
#         result = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)

#         # Print the result
#         logger.info(result.stdout)
#     except Exception as e:
#         logger.error(f"Error occurred while restarting server: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    cmd_command = "python worker.py"
    result = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
    

# logger.info("Starting the server...")
    
# @app.head("/")
# async def head_root():
#     continuous_requests()
#     return JSONResponse(content={"message": "Continuous requests completed."})


@app.get("/keep-alive")
async def keep_alive():
    return JSONResponse(content={"message": "Server is active"})

@app.post("/process-file/")
async def process_file(file: UploadFile = File(...), subject: str = Form(...)):
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Save the uploaded file to the temporary directory
            file_path = os.path.join(tmpdirname, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())

            try:
                # Determine file type and process accordingly
                if file.filename.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
                    response = handle_file(file_path, subject)  # Removed the `model` parameter
                elif file.filename.lower().endswith((".docx", ".doc")):
                    response = "WE ARE UNDER DEVELOPMENT"
                else:
                    raise ValueError("Unsupported file type. Please provide a PDF or image file.")
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        return JSONResponse(content={"response": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
