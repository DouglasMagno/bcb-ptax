FROM python:3.8-slim-buster
WORKDIR /app
#RUN apt-get update
#RUN apt-get install gcc -y
#RUN apt-get install libmariadb-dev-compat libmariadb-dev  -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "-m" , "main"]