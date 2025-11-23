FROM python:3.11-slim

# create app dir
WORKDIR /app

# avoid buffering logs
ENV PYTHONUNBUFFERED=1

# install dependencies
COPY services/premarket/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY services/premarket/app.py .

# copy shared library
COPY shared ./shared

# use entrypoint
CMD ["python", "app.py"]