# 🏠 Real Estate Net

*A modern, scalable real estate marketplace platform built with Django.*

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Installation (3 Steps)

1. **Clone & Setup**
   ```bash
   cd real-estate-net
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install & Configure**
   ```bash
   pip install django django-allauth django-humanize pillow
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

3. **Run Server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access Real Estate Net.

---

## ✨ Key Features

- **🏢 Advanced Property Listings**: Upload photos, floor plans, virtual tours
- **🔍 Smart Search Engine**: Real-time search with advanced filters
- **🗺️ Interactive Maps**: Leaflet-powered property visualization
- **👥 Multi-User System**: Support for brokers, investors, and buyers
- **💎 Premium Features**: Subscription-based enhanced listings
- **📊 Analytics Dashboard**: Comprehensive site management and metrics

---

## 🛠️ Tech Stack

**Backend**: Django 5.2+, PostgreSQL, Celery, Redis
**Frontend**: HTML5, CSS3, JavaScript ES6+, Leaflet Maps
**Deployment**: Docker, AWS S3, Stripe/PayPal integration

---

## 📋 Configuration

Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/real_estate_db
SECRET_KEY=your-secret-key-here
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

---

## 🌐 User Guide

- **Admin Panel**: `/real-admin/` (Superusers only)
- **User Dashboard**: Personalized property management
- **Property Search**: Advanced filters and map view
- **Premium Upgrade**: Subscription-based enhancements

---

## 📁 Structure
```
├── accounts/    # User authentication
├── properties/  # Property management
├── premium/     # Subscriptions & payments
├── analytics/   # Tracking & insights
├── static/      # Assets (CSS, JS, images)
└── templates/   # HTML templates
```

---

## 🚀 Production Deployment

Use Docker Compose for production:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports: ["8000:8000"]
    environment: [DEBUG=False]
```

---

## ℹ️ Important Notes

- **Private Project**: Internal documentation only
- **Security**: Configure HTTPS in production
- **Performance**: Redis caching enabled by default

---

**Real Estate Net** © 2025. Internal development documentation.
