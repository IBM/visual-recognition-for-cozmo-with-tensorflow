FROM tensorflow/tensorflow:1.4.0-py3

# Update repository and install git and zip
RUN apt-get update && \
    apt-get install -y git zip

# Install python requirements for swift
COPY requirements.txt requirements.txt
RUN  pip install -r   requirements.txt

# Get the tensorflow tainingscripts
WORKDIR /
RUN     git clone https://github.com/googlecodelabs/tensorflow-for-poets-2
WORKDIR /tensorflow-for-poets-2

# Copy the runtime script
COPY execscript.sh execscript.sh
RUN  chmod 700 execscript.sh

CMD /tensorflow-for-poets-2/execscript.sh
