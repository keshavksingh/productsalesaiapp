FROM python:3.13.3

WORKDIR /mcp

COPY . .


RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENTRYPOINT ["python", "mcpserver/mcp_server.py"]