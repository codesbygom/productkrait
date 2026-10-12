# ProductKrait — Django E-Commerce With RestApi using DRF and JWT authentication

<p align="center">
  <img src="static/shop/images/logo/productkrait-logo-transparent.png" alt="ProductKrait" width="500">
</p>

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/codesbygom/ProductKrait.git
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ virtualenv env
$ source env/Scripts/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```


Once `pip` has finished downloading the dependencies:
```sh
(env)$ python manage.py runserver

```
And navigate to `http://127.0.0.1:8000/`.


## Running Locally with Docker

Development (runserver with live reload, Postgres in a container, migrations
run on start):

```sh
$ docker compose up --build
```
then view the site at http://localhost:8000/

Production (gunicorn behind nginx, migrations run once by a `migrate`
service). Set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` and
`POSTGRES_PASSWORD` in `.env` first:

```sh
$ docker compose -f docker-compose.prod.yml up -d --build
```
then view the site at http://localhost/

Dependencies are pinned in `requirements.txt`, generated from
`requirements.in`. To add or upgrade one, edit `requirements.in` and run
`uv pip compile requirements.in --python-version 3.14 --python-platform x86_64-unknown-linux-gnu -o requirements.txt`.

## Walkthrough

Copy `.env.example` to `.env` and fill in your own values (a development
fallback is used automatically for anything you leave unset):

```sh
$ cp .env.example .env
```


## Tests

To run the tests, `cd` into the directory where `manage.py` is:
```sh
(env)$ python manage.py test

```
## API Docs 
  navigate to `http://127.0.0.1:8000/swagger/` and `http://127.0.0.1:8000/redoc/`
  
## Features
 rest api using drf,
 jwt authentications,
 django templates,
 html and css
