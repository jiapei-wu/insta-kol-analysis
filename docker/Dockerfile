FROM python:3.8.3

USER root

WORKDIR /instagram-kol-analysis

RUN apt-get update && \
    apt-get install -y \
        ssh \
        libaio1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY /src ./src
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]