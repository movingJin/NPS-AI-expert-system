FROM python:3.10
LABEL maintainer="shdlehdwls@gmail.com"

WORKDIR /app
ADD ./components ./components
ADD ./utils ./utils
COPY ./main.py ./

# Set up virtual environment and install dependencies
RUN pip install streamlit

EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "main.py"]
CMD ["--host=0.0.0.0"]