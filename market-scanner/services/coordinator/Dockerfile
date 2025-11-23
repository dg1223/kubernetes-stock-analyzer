FROM python:3.11-slim

# create app dir
WORKDIR /app

# avoid buffering logs
ENV PYTHONUNBUFFERED=1

# install dependencies
COPY requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY app.py .

# use entrypoint
CMD ['python', 'app.py']