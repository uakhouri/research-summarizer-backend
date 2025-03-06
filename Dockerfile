#Use python 3.10 or lates
FROM python:3.13

#Set the working directory
WORKDIR /app

#cCopy the backend files
COPY requirements.txt requirements.txt

COPY . .

# Ensure pip is installed and updated properly
# RUN python -m ensurepip --upgrade
# RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

#Install Dependencies
RUN pip install -r requirements.txt

#Expose PORT 8080 for CLoud Run
EXPOSE 8080

#Start FASTApi with uvicorn

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]