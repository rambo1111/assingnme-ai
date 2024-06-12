import os
import re
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import tempfile
import fitz  # PyMuPDF
from PIL import Image
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import subprocess

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def handle_file(file_path, subject):
    image_files = []

    if file_path.lower().endswith('.pdf'):
        with fitz.open(file_path) as pdf_document:
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(10.0, 10.0))
                image_file = f'page_{page_num + 1}.png'
                pix.save(image_file)
                image_files.append(image_file)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_files.append(file_path)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_path}")
        
    
    GOOGLE_API_KEY = 'AIzaSyA69r6qP6dBD1agDCBYgf1fk4xMNLogovk'
    genai.configure(api_key=GOOGLE_API_KEY)

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    }
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    extracted_text = ""

    # Process each image with the generative model
    for image_file in image_files:
        image = Image.open(image_file)
        result = model.generate_content(['''EXTRACT TEXT FROM IT,
                                         IF IT'S IN A TABLE EXTRACT THE TABLE,
                                         IF THERE IS A DIAGRAM SUMMARIZE THE DIAGRAM''', image],
                                         safety_settings=safety_settings)
        extracted_text += result.text + "\n\n"

    # Process the extracted text with the generative model    
    response = model.generate_content(
        [f'''I have extracted text from a pdf, which is my {subject} assignment. Please answer these questions:{extracted_text}.
             NOTE: 1. Start every answer with Ans1-, next with Ans2- and so on.
                   2. Don't use to **bold** or *italics* or ## for headings, just normal text without any markdown.
                   3. You can use a line break for next line.
                   4. If the question says to draw a diagram don't draw it.'''],
        safety_settings=safety_settings
    )
    
    return response.text

def sanitize_filename(filename):
    # Split the filename and extension
    name, extension = os.path.splitext(filename)
    # Remove special characters from the filename
    sanitized_name = re.sub(r'[^\w\-_.]', '', name)
    # Generate a random string to prevent filename collisions
    random_string = str(uuid.uuid4())[:8]
    # Concatenate the sanitized name, original extension, and random string
    return f"{sanitized_name}_{random_string}{extension}"

    
@app.on_event("shutdown")
async def shutdown_event():
    cmd_command = "python worker.py"
    result = subprocess.run(cmd_command, shell=True, capture_output=True, text=True)
    

# logger.info("Starting the server...")
    
@app.head("/")
async def head_root():
    logger.info("Server started")


@app.get("/keep-alive")
async def keep_alive():
    return JSONResponse(content={"message": "Server is active"})

@app.post("/process-file/")
async def process_file(file: UploadFile = File(...), subject: str = Form(...)):
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Sanitize the filename
            safe_filename = sanitize_filename(file.filename)
            # Save the uploaded file to the temporary directory
            file_path = os.path.join(tmpdirname, safe_filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())

            print(f"Uploaded file: {file_path}")  # Add debugging statement

            # Handle the file
            response = handle_file(file_path, subject)

            return JSONResponse(content={"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
