FROM tensorflow/tensorflow:1.4.0-py3

WORKDIR /tensorflow
COPY requirements.txt requirements.txt
RUN  pip install -r   requirements.txt

COPY classifier.py classifier.py

CMD python -u classifier.py
