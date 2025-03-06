#Use python 3.10 or lates
FROM python:3.13

#Set the working directory
WORKDIR /app

#cCopy the backend files
COPY . /app

# Ensure pip is installed and updated properly
RUN python -m ensurepip --upgrade
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

#Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Expose PORT 8080 for CLoud Run
EXPOSE 8080

#Start FASTApi with uvicorn
CMD [ "gunicorn", "-w","4","-k","uvicorn.workers.UvicornWorker","main:app","--bind","0.0.0.0:8080"]