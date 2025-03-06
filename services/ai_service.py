#This file contains the logic for AI-powered summarization using OpenAI's GPT-4.

import openai
from transformers import pipeline, AutoTokenizer
import os
from dotenv import load_dotenv

#loading the env variables
load_dotenv()

#Set your OpenAI key
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
  raise ValueError("OpenAI API Key is missing!")

#Using a Hugging Face summarization model
model_name = "facebook/bart-large-cnn"
summarizer = pipeline("summarization", model=model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)



def split_text_into_chunks(text, max_tokens=512):
    """
    Splits text into chunks that fit within the model's token limit.
    Uses Pegasus' tokenizer to ensure chunks are safe.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        # Add word to current chunk
        current_chunk.append(word)

        # Check token length after adding the word
        token_count = len(tokenizer(" ".join(current_chunk))['input_ids'])

        # If token limit is exceeded, finalize current chunk and start a new one
        if token_count > max_tokens - 10:  # Keeping a buffer of 10 tokens
            chunks.append(" ".join(current_chunk[:-1]))  # Save previous chunk
            current_chunk = [word]  # Start new chunk with last word

      # Add last chunk if not empty
    if current_chunk:
          chunks.append(" ".join(current_chunk))

    return chunks


def generate_summary(text:str, use_gpt:bool=False):
  """
    Generates a summary of the given text using either GPT - 4 or Hugging Face Model
  """

  min_text_length = 50
  max_input_length = 512

  if not text or len(text.strip())<min_text_length:
    return f"Error: Input text is too short ({len(text.strip())} chars). Try a longer document."
  
  #Split long text into manageable chunks
  text_chunks = split_text_into_chunks(text, max_tokens=max_input_length)

  print(f"[DEBUG] Splitting text into {len(text_chunks)} chunks for summarization.")

  if use_gpt:
    client = openai.OpenAI()
    response = client.chat.completions.create(
      model = "gpt-4o",
      messages=[{"role":"user", "content":f"Summarize this research paper:\n{text}"}],
      max_tokens=1000
    )
    return response.choices[0].message.content
  
  else:
    summaries=[]
    for i,chunk in enumerate(text_chunks):
      print(f"[INFO] Summarizing chunk {i+1}/{len(text_chunks)}...")
      try:

        # # Ensure max_length is within safe limits
        # tokenized_input = tokenizer(chunk, return_tensors="pt")
        # input_token_count = tokenized_input["input_ids"].shape[1]
        
        # #Adjust max_length dynamically to prevent index errors
        # # text_length = len(chunk.split())
        # max_summary_length = min(150, int(input_token_count*0.5))
        # min_summary_length = max(50,int(max_summary_length*0.5))

        # max_summary_length = max_input_length  # Keep summary ~50% of input
        # min_summary_length = min_text_length  # Ensure valid min_length



        summary = summarizer(chunk, max_length = 150, min_length =50, do_sample = False)
        summaries.append(summary[0]['summary_text'])
      except IndexError as e:
        summaries.append(f"Error: {str(e)} - Input text may be too short.")
      except Exception as e:
        summaries.append(f"Error: {str(e)}")
    return " ".join(summaries)