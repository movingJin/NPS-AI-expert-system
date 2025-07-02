FROM python:3.10
LABEL maintainer="shdlehdwls@gmail.com"

WORKDIR /app
ADD ./db ./db
ADD ./retrieval ./retrieval
ADD ./routers ./routers
ADD ./utils ./utils
ADD ./workflow ./workflow
COPY ./.env ./
COPY ./data.pdf ./
COPY ./main.py ./

# Set up virtual environment and install dependencies
RUN pip install fastapi uvicorn python-dotenv
RUN pip install langchain==0.3.26 langgraph==0.5.0 langfuse==2.59.7 langchain-openai==0.3.27 langchain-community==0.3.26 pydantic-settings==2.10.1 pdfplumber==0.11.7 PyMuPDF==1.26.1

EXPOSE 8082
ENTRYPOINT ["python", "main.py"]
CMD ["--host=0.0.0.0"]