FROM kennethreitz/pipenv

WORKDIR /lounas
COPY . .
RUN pipenv install

CMD pipenv run python3 app.py
