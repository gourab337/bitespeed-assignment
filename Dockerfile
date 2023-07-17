FROM public.ecr.aws/ubuntu/ubuntu:edge as builder

RUN apt update && apt upgrade
RUN apt install curl --yes
RUN apt-get install python3-pip --yes
RUN mkdir -p /app
WORKDIR /app
COPY . .
RUN ls
RUN apt install --yes python3.11-venv
RUN python3 -m venv .venv
RUN . .venv/bin/activate
RUN pip3 install -r requirements.txt --break-system-packages
RUN python3 run_db_query.py
RUN python3 identity_reco.py
EXPOSE 3232
