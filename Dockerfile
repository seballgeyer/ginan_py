#FROM python:3.12.0-bullseye
#LABEL authors="sebastien"
#
##RUN apk add gcc libc-dev linux-headers
#
#WORKDIR /app
#COPY   requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#
#ARG INSTALL_JUPYTER=false
#RUN sh -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"
#
#ARG INSTALL_DEV=false
#RUN if [ $INSTALL_DEV == 'false' ] ; then \
#    pip install -e . ; \
#else \
#    echo '/app/src' >> /usr/local/lib/python3.12/site-packages/pythonpath.pth ; \
#fi
#
#COPY . .
#WORKDIR /app/api
#CMD [ "flask", "--app", "manage:app", "run" ,"--debug"]

FROM python:3.12-alpine3.18
LABEL authors="sebastien"

RUN apk add gcc libc-dev linux-headers

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ARG INSTALL_JUPYTER=false
RUN sh -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"

ARG INSTALL_DEV=false
RUN if [ $INSTALL_DEV == 'false' ] ; then \
    pip install -e . ; \
else \
    echo '/app/src' >> /usr/local/lib/python3.12/site-packages/pythonpath.pth ; \
fi

COPY . .
WORKDIR /app/api
CMD [ "flask", "--app", "manage:app", "run" ,"--debug", "-p", "8889"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]