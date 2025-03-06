# This file defines the API routes.

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Query
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from services.ai_service import generate_summary
from services.pdf_service import extract_text_from_pdf
from services.paper_extraction import search_arxiv,search_google_scholar


app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ["*"]
)


class SummarizationRequest(BaseModel):
  text:str
  use_gpt:bool=False


#Default Route
@app.get("/")
def home():
  return{"message":"AI Research Platform is running!"}


#Route for summarizing the paper (copy+paste)
@app.post("/summarize")
def summarize_text(request:SummarizationRequest):
  if not request.text:
    raise HTTPException(status_code=400, detail="Text cannot be empty")
  
  summary = generate_summary(request.text,request.use_gpt)

  return {"summary":summary}

#Route for summarizing the paper (pdf upload)


#Creating a folder to save the uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok= True)

@app.post("/upload-pdf/")
async def upload_pdf(file:UploadFile = File(...), use_gpt:bool=Form(False)):
  """
    Upload a PDF File, extract its text, and summarize it
  """

  if not file.filename.endswith(".pdf"):
    raise HTTPException(status_code=400, detail="Only PDF Files are allowed.")
  
  file_path = os.path.join(UPLOAD_FOLDER, file.filename)

  #Save file temporarily
  with open(file_path,"wb") as f:
    f.write(file.file.read())

  #Extract text from pdf
  extracted_text = extract_text_from_pdf(file_path)

  if not extracted_text:
    raise HTTPException(status_code=400,detail="Could not extract text from PDF.")
  
  print(f"Extracted Text (first 500 chars):\n{extracted_text[:500]}")  # Debugging print
  
  #Summarize extracted text
  summary = generate_summary(extracted_text,use_gpt)

  return {"summary":summary}


# Summarizing academic papers
# @app.get("/search/google-scholar/")
# async def google_scholar_search(query:str,num_results:int= Query(5, ge=1, le=10)):
#   """
#   Fetches academic papers from google scholar
#   """

#   return{"papers":search_google_scholar(query, num_results)}

@app.get("/search/arxiv/")
async def arxiv_search(query:str,num_results:int = Query(5, ge=1, le=10)):
  """
  Fetches academic papers from arxiv
  """

  return {"papers":search_arxiv(query,num_results)}

@app.get("/search-and-summarize/")
async def search_and_summarize(
  source:str = Query(...,description="Source:arxiv"),
  query:str = Query(...,description="Search Query"),
  num_results:int = Query(3,ge=1, le=10),
  use_gpt:bool=Query(False,description="Use GPT-4o if true, otherwise LED")
):
  """
  Searches academic papers and summarizes them
  """
  if source=="arxiv":
    papers = search_arxiv(query, num_results)

  summarized_papers=[]
  for paper in papers:
    summary = generate_summary(paper['title']+"\n"+paper.get("abstract",""), use_gpt)
    paper["summary"] = summary
    summarized_papers.append(paper)

  return {"papers":summarized_papers}