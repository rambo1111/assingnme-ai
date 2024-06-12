from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import tempfile
import fitz  # PyMuPDF
from PIL import Image
import os
from google.generativeai.types import HarmCategory, HarmBlockThreshold
# import requests


app = FastAPI()

# Configure CORS to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
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
        raise HTTPException(status_code=400, detail="Unsupported file format. Please provide a PDF or an image file.")    
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
            file_path = os.path.join(tmpdirname, secure_filename(file.filename))
            with open(file_path, "wb") as f:
                f.write(await file.read())

            # Handle the file
            response = handle_file(file_path, subject)

            return JSONResponse(content={"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
