FROM python:3-slim
WORKDIR /code

# Copy Pipfile related files
COPY Pipfile.lock /code/
COPY Pipfile /code/

# Install dependencies
RUN pip install pipenv && pipenv install --system --deploy

# Default command to run app
CMD gunicorn api.py -b 0.0.0.0:${PORT:-5000} -w 3

# Copy codebase to docker image
COPY . /code
