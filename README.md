# ProductKrait — Django E-Commerce With RestApi using DRF and JWT authentication

<p align="center">
  <img src="backend/static/shop/images/logo/productkrait-logo-transparent.png" alt="ProductKrait" width="500">
</p>

## Project layout

```
backend/    Django project (shop, account, manager panel, DRF + JWT API, Docker)
frontend/   Next.js app that uses the backend API (see frontend/.env.example)
```

Every backend command below is run from the `backend/` folder. The frontend:

```sh
$ cd frontend && npm install && npm run dev
```

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/codesbygom/ProductKrait.git
$ cd ProductKrait/backend
```

You need Python 3.13 (the same version the Docker image uses). On Windows,
get it with the official
[Python Install Manager](https://www.python.org/downloads/windows/)
(`py install 3.13`).

Create a virtual environment to install dependencies in and activate it:

```sh
$ py -V:3.13 -m venv venv           # macOS/Linux: python3.13 -m venv venv
$ venv\Scripts\activate             # macOS/Linux: source venv/bin/activate
```

Then install the dependencies:

```sh
(venv)$ pip install -r requirements.txt
```


Once `pip` has finished downloading the dependencies:
```sh
(venv)$ python manage.py runserver

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
(venv)$ python manage.py test

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
- **Shop** (Django templates): categories (nested menu), search, product
  pages, cart, checkout with Zarinpal payment, order history.
- **Account**: sign up (logs you straight in), log in, profile with
  shipping details (pre-fills checkout), change password, "forgot
  password" email reset.
- **Manager panel** (`/manage/`, staff only): dashboard (stock, orders,
  customers, revenue, recent orders), products, categories, orders,
  customers (search, order/payment history, block / unblock) and payments.
- **REST API** with DRF + JWT (see API Docs above).
- **Caching** of the category menu and catalogue API responses, invalidated
  automatically when products or categories change.

## Cache (Redis / PythonAnywhere)

The cache backend is one setting, `CACHE_BACKEND` in `.env`:

| Value | Backend | When to use |
|---|---|---|
| `redis` | Redis at `REDIS_URL` | Docker (`docker compose up` starts a `redis` service and sets `REDIS_URL`) |
| `file` | Django file cache in `CACHE_DIR` | **PythonAnywhere** (no Redis there; shared by all web workers) |
| `db` | Django database cache | run `python manage.py createcachetable` once |
| `locmem` | Django in-process cache | local development |
| `dummy` | no caching | debugging |

Leave it empty and it picks `redis` when `REDIS_URL` is set, `locmem`
otherwise. If Redis goes down the site keeps working, just uncached.
On PythonAnywhere put these in the WSGI file (or `.env`):

```sh
CACHE_BACKEND=file
CACHE_DIR=/home/<your-username>/ProductKrait/.cache
```

## Deploying to PythonAnywhere

Same flow as a standard Django app (no Docker, no Redis):

1. Clone the repo in a Bash console, then
   `mkvirtualenv --python=/usr/bin/python3.13 productkrait-env && pip install -r backend/requirements.txt`.
2. Web tab → *Add a new web app* → **Manual configuration** → Python 3.13, and set the virtualenv path.
3. In the WSGI file, add the project to `sys.path` and set the environment before importing Django:

   ```python
   import os, sys
   path = '/home/<your-username>/ProductKrait/backend'
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'ProductKrait.settings'
   os.environ['DJANGO_SECRET_KEY'] = '<generated key>'
   os.environ['DJANGO_DEBUG'] = 'False'
   os.environ['DJANGO_ALLOWED_HOSTS'] = '<your-username>.pythonanywhere.com'
   os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = 'https://<your-username>.pythonanywhere.com'
   os.environ['CACHE_BACKEND'] = 'file'
   os.environ['CACHE_DIR'] = '/home/<your-username>/ProductKrait/backend/.cache'
   os.environ['PAYMENT_BACKEND'] = 'mock'   # free fake bank page; 'zarinpal' needs a paid account
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
4. `cd backend && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py createsuperuser`.
5. Static files: `/static/` → `.../backend/staticfiles`, `/media/` → `.../backend/media`. Reload.

With `DJANGO_DEBUG=False` the app refuses to start on the dev secret key or
empty `DJANGO_ALLOWED_HOSTS`, forces HTTPS and sets secure cookies. Free
accounts can only reach whitelisted sites, so Zarinpal can't be called there:
this branch ships a built-in **mock payment gateway** (`PAYMENT_BACKEND=mock`,
the default here) with a fake bank page where you choose "Pay" or "Simulate
failure". No money, no sign-up, no outbound requests. Set
`PAYMENT_BACKEND=zarinpal` to use the real gateway again. The Next.js `frontend/` can't run on
PythonAnywhere: host it elsewhere (e.g. Vercel) with `BACKEND_URL` and
`NEXT_PUBLIC_BACKEND_URL` set to the PythonAnywhere URL.
