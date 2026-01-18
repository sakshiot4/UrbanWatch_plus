# 🏙️ UrbanWatch+

### Civic Issue Reporting & Tracking System

**UrbanWatch+** is a web-based platform designed to bridge the gap between citizens and municipal authorities. It allows users to report local infrastructure issues (like sanitation, potholes, or streetlights) and tracks the resolution process through a transparent, multi-role workflow.

---

## 🚀 Key Features

* **📢 Report & Track:** Citizens can lodge complaints with descriptions and images. Each complaint generates a unique **Tracking Token (UUID)** for public status tracking without logging in.
* **📍 Geolocation Integration:** precise location mapping using **Leaflet.js**, automatically assigning issues to the correct municipal ward/region based on coordinates or pincode (Focused on Mumbai region).
* **👥 Role-Based Access Control (RBAC):** Distinct dashboards for different users:
    * **Citizens:** Report issues and view history.
    * **Officers:** Validate complaints and assign them to contractors.
    * **Contractors:** View assigned tasks and upload "Proof of Work" to mark completion.
* **🔄 Automated Workflow:** A state-machine approach to issue resolution (Reported -> Verified -> Assigned -> Resolved).
* **🔐 Secure Authentication:** Robust user management using **Django-Allauth**.

## 🛠️ Tech Stack

* **Backend:** Python, Django 5
* **Database:** SQLite (Development) / PostgreSQL (Production ready)
* **Frontend:** HTML5, CSS3, Tailwind CSS, JavaScript
* **Mapping:** Leaflet.js / OpenStreetMap
* **Authentication:** Django Allauth


## ⚙️ Installation & Setup

If you want to run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/sakshiot4/UrbanWatch_plus.git]
    cd UrbanWatch
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

6.  **Access the app:**
    Open your browser and go to `http://127.0.0.1:8000/`

## 🤝 Contributing

This project is currently in active development. Suggestions and feedback are welcome!

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature-name`)
3.  Commit your changes (`git commit -m "Added new feature"`)
4.  Push to the branch (`git push origin feature-name`)
5.  Create a Pull Request

---

**Developed by Sakshi Sawant**
