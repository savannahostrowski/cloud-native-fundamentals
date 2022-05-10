FROM python:3.8
LABEL maintainer="Savannah Ostrowski"

COPY techtrends /app
WORKDIR /app

EXPOSE 3111

RUN pip install -r requirements.txt

CMD ["sh", "-c", "python init_db.py && python app.py"]
