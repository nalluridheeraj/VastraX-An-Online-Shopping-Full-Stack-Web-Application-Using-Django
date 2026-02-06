# VastraX – Fashion E‑commerce Webapp

VastraX is a full-stack fashion e-commerce web application built with **HTML, CSS, JavaScript, Django, and MySQL**.

## Features

- **Single login page** for both User and Admin/Manager (OTP via email, with “Login as User” / “Login as Admin”).
- **User:** Register (with welcome email), browse products, sort/filter (price, rating, gender, category, product type), cart, checkout, coupons, addresses, orders.
- **Admin (separate app):** Dashboard (sales, orders per product), manage products (add/edit/delete, stock), manage orders, manage users, coupons, and offers (e.g. 35% off on a product). No Django admin required.
- **Security:** Only admin session can access `/adminapp/`; regular users get “Access denied” if they try.

## Project structure

- **mainapp** – Home, About, Contact, Collections (Men / Women / Kids), product listing with sort & filter, product detail.
- **userapp** – Login (OTP), Register (welcome email), Cart, Checkout, Orders, Addresses, Coupons.
- **adminapp** – Dashboard, Products, Orders, Users, Coupons, Offers (separate UI, not Django admin).

## Setup

### 1. Python & MySQL

- Python 3.10+
- MySQL server (create a database, e.g. `vastrax_db`)

### 2. Install dependencies

```bash
cd vastrax
pip install -r requirements.txt
```

### 3. Database

Edit `vastrax_project/settings.py` if needed:

- `DATABASES['default']`: `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` (default `3306`).

Create the database in MySQL:

```sql
CREATE DATABASE vastrax_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Migrations

```bash
python manage.py makemigrations mainapp userapp adminapp
python manage.py migrate
```

### 5. Create first admin user (for OTP admin login)

In Django shell:

```bash
python manage.py shell
```

```python
from adminapp.models import AdminUser
AdminUser.objects.create(name='Admin', email='admin@example.com', password='your_password')
exit()
```

Use this email on the **Login** page, choose **Login as Admin / Manager**, then **Send OTP**. Check your email for the OTP.

### 6. Email (OTP and welcome mail)

Set in `vastrax_project/settings.py` or environment:

- `EMAIL_HOST_USER` – sender email (e.g. Gmail).
- `EMAIL_HOST_PASSWORD` – app password (for Gmail use an App Password).

### 7. Static and media

- Place images in `static/images/` as per `static/images/README.txt` (logo, login-bg, register-bg, mens-bg, womens-bg, etc.).
- Media uploads (product images, profiles) go to `media/` (created automatically).

### 8. Run server

```bash
python manage.py runserver
```

- Site: http://127.0.0.1:8000/
- Admin area (after admin OTP login): http://127.0.0.1:8000/adminapp/dashboard/

## Navigation

- **Main site:** Home, Collections, Men, Women, Kids, About, Contact, Login, Join Now (Register). Current page is highlighted in the nav. Logo on the left.
- **Login/Register:** Form on the right; each page has its own background image.
- **Collections:** Men’s and Women’s use blur background images with product cards on overlay; Kids uses a light-themed default image. Sort by price/rating, filter by type/category.

## Notes

- If a **user** tries to open admin URLs or chooses “Login as Admin” with a **user** email, they get “Invalid Credentials” or “Access denied” as designed.
- All admin tasks (products, orders, users, coupons, offers) are done from the **adminapp** web UI only, not from Django’s `/admin/` backend.
