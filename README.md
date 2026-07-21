# PLUS ERP

<p align="center">
  <img src="https://raw.githubusercontent.com/EduardoMartinez68/MANUAL_ERP_PLUS/main/assets/logo.png" alt="PLUS ERP" width="180">
</p>

<p align="center">
  <strong>Modern, modular and open-source ERP built with Django.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.x-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/Django-Latest-success.svg" alt="Django">
</p>

---

# PLUS ERP

PLUS ERP is a modular Enterprise Resource Planning (ERP) system developed with **Django**. It is designed to provide a scalable foundation for managing businesses through independent modules, making it easy to extend and customize according to different industries.

---

# 📖 User Manual

The complete user manual is available in this repository:

➡️ **https://github.com/EduardoMartinez68/MANUAL_ERP_PLUS**

There you will find:

- Installation guide
- User documentation
- Module explanations
- Configuration examples
- Screenshots
- Frequently asked questions

---

# 🚀 Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/EduardoMartinez68/PLUS_ENGINE_ERP
cd PLUS
```

---

## 2. Install dependencies

All Python dependencies are listed in:

```
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

---

## 3. Configure environment variables

Create a new file named:

```
.env
```

Copy all variables from:

```
example.env
```

If you only want to make a quick local test, configure these variables:

```env
TYPE_VERSION=DESKTOP
TYPE_DATABASE=SQLITE
```

Using these settings, PLUS ERP will automatically use a local **SQLite** database.

---

## 4. Create the database

Generate migrations (only when creating a new app or models):

```bash
python manage.py makemigrations [APP_NAME]
```

Apply migrations:

```bash
python manage.py migrate
```

---

## 5. Start the development server

Default:

```bash
python manage.py runserver
```

Or allow connections from other devices on your network:

```bash
python manage.py runserver 0.0.0.0:8000
```

---

# 🐳 Docker

A ready-to-use **Dockerfile** is included in this project.

You can build and run the application using Docker according to your deployment needs.

---

# 📁 Project Structure

```
PLUS/
│
├── apps/
├── core/
├── static/
├── templates/
├── media/
├── requirements.txt
├── Dockerfile
├── example.env
├── .env
└── manage.py
```

---

# ⚙️ Requirements

- Python 3.x
- Django
- pip
- Virtual Environment (recommended)

---

# 📦 Dependencies

All required packages are located in:

```
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

---

# 🔧 Environment Configuration

Configuration is managed through the `.env` file.

For development using SQLite:

```env
TYPE_VERSION=DESKTOP
TYPE_DATABASE=SQLITE
```

For production, configure the remaining variables according to your infrastructure.

---

# 🤝 Contributing

Contributions are welcome!

If you would like to improve PLUS ERP:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

# 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

See the `LICENSE` file for more information.

---

# 👨‍💻 Author

**Martinez Ortiz Eduardo Antonio**

Software Engineer

---

## ⭐ Support the Project

If this project is useful to you, consider giving it a ⭐ on GitHub.