FROM python:latest

RUN pip install --upgrade pip && \
    pip install --upgrade setuptools


RUN pip install --upgrade MAVProxy

RUN mkdir -p "/companion && \
    mkdir -p /var/log/companion/
WORKDIR /companion
COPY ./app/* .

RUN pip install -f requirement.txt

RUN for script in $(ls ./*.sh) ; do \
        chmod +x ${script} && \
        dest=$(basename $(echo ${script} | sed 's#.sh##g')) && \
        mv -v ${script} /usr/bin/${dest} && \
        echo "SCRIPT: ${script} > /usr/bin/${dest}" >> /var/log/build.log \
    ; done

ENTRYPOINT [ "run" ]
CMD [ ]