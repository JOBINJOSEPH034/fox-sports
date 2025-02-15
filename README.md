# Fox Sports - E-commerce Platform

## Project Overview
**Fox Sports** (https://jofox.shop) is a feature-rich e-commerce platform specializing in sports items. Built with Django (Python) and PostgreSQL, the platform is hosted on AWS with Nginx and Gunicorn running on Ubuntu. The frontend is designed using HTML, CSS, Bootstrap, and JavaScript.

## Features
### User Features:
- **Shop Page**: Search, filter, and sort products by different options.
- **Product Details Page**: Displays current offers, different variants, available stock, brand name, category, and wishlist functionality.
- **Cart Page**:
  - Increase/decrease stock quantity
  - Apply and remove available coupons
- **Checkout Page**:
  - Payment options: **Cash on Delivery (COD)**, **Wallet**  and **Razorpay Online Payment**
  - Add wallet balance via **Razorpay Integration**
- **Profile Page**:
  - Manage profile details
  - View order history with downloadable invoices (PDF format)
  - Address management
  - Wallet (add funds via Razorpay)
  - Wishlist
  - Change password

### Admin Features:
- **Admin Dashboard**:
  - Graphical representation of orders (daily, weekly, monthly, yearly)
  - Filter sales data by different timeframes
  - Display top-selling brands, categories, and products
- **Product Management**: Add/edit products
- **Customer Management**: Block/unblock customers
- **Category Management**: Add/edit/block categories
- **Brand Management**: Add/edit brands
- **Offer Management**: Add/edit offers
- **Coupon Management**: Add/edit/remove coupons
- **Order Management**: Process orders, manage returns
- **Inventory Management**: Track product stock
- **Sales Reports**:
  - Generate full sales reports
  - Export data to **Excel & PDF**


## Technology Stack
### Backend:
- **Django (Python)**
- **PostgreSQL**
- **Gunicorn**
- **Ubuntu Server**

### Frontend:
- **HTML, CSS, Bootstrap, JavaScript**

### Server & Hosting:
- **AWS (Amazon Web Services)**
- **Nginx** (Reverse proxy)

## Installation & Setup
### Prerequisites:
- Python 3.x
- PostgreSQL
- Git
- Virtual Environment

### Setup Steps:
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fox-sports
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure `.env` file**:
   - Set up database credentials
   - Configure Razorpay API keys
   - Add AWS deployment settings
5. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```
6. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```
7. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

## Deployment (AWS + Nginx + Gunicorn)
1. **Set up PostgreSQL database**
2. **Install and configure Nginx** (as a reverse proxy)
3. **Set up Gunicorn for running Django application**
4. **Configure domain (jofox.shop) and SSL (Let's Encrypt)**
5. **Deploy using Git and restart services**:
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

## Troubleshooting
- **Gunicorn/Nginx not responding?** Check logs:
  ```bash
  sudo journalctl -u gunicorn --no-pager --lines=50
  sudo journalctl -u nginx --no-pager --lines=50
  ```
- **Database errors?** Verify PostgreSQL connection:
  ```bash
  sudo systemctl status postgresql
  ```
- **Static files not loading?** Run:
  ```bash
  python manage.py collectstatic --noinput
  ```

## License
This project is licensed under the MIT License.

## Author
**Jobin** - Developer & Founder of Fox Sports

---
Feel free to modify the content based on your specific deployment and additional features!

