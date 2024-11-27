FROM python 
WORKDIR /code
COPY . /code
RUN apt-get update && apt-get install -y libgl1 tesseract-ocr
RUN pip install -r requirements.txt --use-deprecated=legacy-resolver
CMD [ "python3", "MotorEase.py" ]
