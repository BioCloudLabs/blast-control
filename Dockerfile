FROM python:3.10-alpine
RUN pip install --upgrade pip
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . /app
EXPOSE 4000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:4000", "app:app"]