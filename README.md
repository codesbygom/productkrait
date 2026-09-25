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

1.build the image:

```sh
  $ docker-compose build .
```
2.Spin up the containers
```sh
  $ docker-compose up
```
then view the site at  http://localhost:8000/

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

Authenticate with `Authorization: Bearer <access token>` (JWT). Catalogue
reads are public; product/category writes are staff-only.

| Method | Endpoint | What it does |
|---|---|---|
| POST | `/api/account/register/` | sign up (sends a verification mail) |
| POST | `/api/account/token/` · `token/refresh/` · `token/verify/` | JWT obtain (email + password) / refresh / verify |
| POST | `/api/account/logout/` | blacklist a refresh token |
| GET / PATCH | `/api/account/profile/` | view / edit your profile |
| POST | `/api/account/request-verification/` | resend the verification mail |
| GET | `/api/account/verify-email/<token>/` | verify your email (the link in the mail) |
| POST | `/api/account/forget-password/` | mail a password-reset link |
| PUT | `/api/account/reset-password/<uidb64>/<token>/` | set a new password from the link |
| PUT | `/api/account/change-password/` | change password |
| GET / POST | `/api/shop/products/` | list (`?category=`, `?search=`, `?in_stock=true`, `?ordering=price`) / create |
| GET / PATCH / DELETE | `/api/shop/products/<id>/` | product detail / edit / delete |
| GET / POST | `/api/shop/category/` | categories (`?root=true` for top level) / create |
| GET / PATCH / DELETE | `/api/shop/category/<slug>/` | category with its products and children |
| GET / DELETE | `/api/shop/cart/` | your cart / empty it |
| POST | `/api/shop/cart/items/` | add `{product_id, quantity}` |
| PATCH / DELETE | `/api/shop/cart/items/<product_id>/` | set quantity (0 removes) / remove |
| GET | `/api/shop/orders/` · `orders/<id>/` | your order history |
| GET | `/api/shop/latest_products/`, `/api/shop/categories/`, `/api/shop/search/?query=` | original endpoints, still available |

Emails are printed to the console unless `EMAIL_BACKEND` and the SMTP
settings in `.env` point somewhere real.
  
## Features
 rest api using drf,
 jwt authentications,
 django templates,
 html and css
