# 🏠 Gorkha Real Estate

A modern real estate platform built with Django for property listings, user management, and premium services in Nepal.

## 🚀 Quick Start

### Requirements
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/real-estate-net.git
   cd real-estate-net
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv real_estate_env
   # Windows:
   real_estate_env\Scripts\activate
   # macOS/Linux:
   source real_estate_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**
   ```bash
   python manage.py migrate
   ```

5. **Create admin user** (optional for development)
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to access the website!

## ✨ Features

- **🏢 Property Management**: List and manage real estate properties
- **👤 User Authentication**: Sign up, login, and user profiles
- **🔍 Advanced Search**: Filter properties by location, price, type
- **💎 Premium Services**: Subscription-based premium listings
- **📊 Analytics Dashboard**: Track website performance
- **📱 Responsive Design**: Mobile-friendly interface
- **📰 Blog**: Property news and market updates
- **📞 Contact System**: Inquire about properties

## 📁 Project Structure

```
├── accounts/         # User authentication and profiles
├── properties/       # Property listings and management
├── premium/          # Premium subscription features
├── analytics/        # Website analytics and tracking
├── contact/          # Contact forms and inquiries
├── blog/            # Blog articles and posts
├── legal/           # Legal pages and agreements
├── static/          # CSS, JavaScript, and images
├── templates/       # HTML templates
└── real_estate/     # Django project settings
```

## 🛠️ Tech Stack

- **Backend**: Django 5.2.7
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Django Allauth (social login support)
- **Forms**: Django Crispy Forms

## 📝 Environment Variables

Create a `.env` file in the project root with your configuration:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License



**Made with ❤️ for the real estate community in Nepal**
