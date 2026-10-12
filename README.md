# E-Commerce Backend API Using FastAPI

## 📌 Project Overview

This project is a backend REST API for an E-commerce application developed using **Python and FastAPI**. It provides essential e-commerce functionalities, including user authentication, role-based access control, product management, shopping cart operations, order processing, coupon-based discounts, and payment management.

The application uses SQLAlchemy for database operations and SQLite for data storage. JWT-based authentication and password hashing are implemented to manage user sessions and protect authorized endpoints.

## ✨ Features

- **User Authentication:** User registration and login with password hashing and JWT token generation.
- **Role-Based Access Control (RBAC):** Separate access permissions for Buyers, Sellers, and Admins.
- **User Management:** User profile access and administrative role management.
- **Product Management:** Create, retrieve, update, and manage product information.
- **Shopping Cart:** Add products to a cart and manage product quantities.
- **Order Management:** Create orders, store order items, and maintain order history and status.
- **Promotions and Coupons:** Apply discount codes based on minimum purchase amounts, expiry dates, and active status.
- **Payment Management:** Payment-related records, transaction details, and Razorpay test integration components.
- **Database Integration:** SQLAlchemy ORM with SQLite for storing users, products, carts, orders, promotions, and payments.
- **API Documentation:** Interactive API documentation through FastAPI's Swagger UI.

## 🛠️ Tech Stack

- **Programming Language:** Python
- **Backend Framework:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **Authentication:** JWT and OAuth2 Bearer tokens
- **Password Security:** Password hashing and verification
- **Payment Integration:** Razorpay test integration components
- **API Documentation:** Swagger UI

## ⚙️ How to Run the Project

1. Clone the repository:

   ```bash
   git clone YOUR_GITHUB_REPOSITORY_URL
   ```

2. Navigate to the project directory:

   ```bash
   cd fastapi-project-main
   ```

3. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   On Windows:

   ```bash
   venv\Scripts\activate
   ```

4. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

6. Open the interactive API documentation:

   ```text
   http://127.0.0.1:8000/docs
   ```

## 🎯 Learning Outcomes

Through this project, I gained practical experience in building REST APIs, implementing JWT authentication, managing user roles and permissions, working with relational databases using SQLAlchemy, validating request data with Pydantic, and organizing backend application logic.

## 🚀 Future Enhancements

- Add automated testing for API endpoints.
- Improve configuration and secret management using environment variables.
- Add production-ready payment verification.
- Implement stronger authorization checks for resource ownership.
- Deploy the application to a cloud platform.

---

**Project Type:** Backend Development | REST API | E-commerce  
**Status:** Development Project
