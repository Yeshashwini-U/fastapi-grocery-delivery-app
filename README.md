🛵 FreshMart Grocery Delivery API (FastAPI)
📌 Project Overview

FreshMart is a backend API built using FastAPI that simulates a real-world grocery delivery system.
It allows users to browse grocery items, add them to a cart, place orders, and manage deliveries with advanced features like filtering, sorting, and pagination.

This project was developed as part of a FastAPI Internship Final Project, covering all core backend concepts from Day 1 to Day 6.

🚀 Features Implemented
✅ Day 1 — GET APIs

Home route (/)

Get all items (/items)

Get item by ID (/items/{item_id})

Items summary (/items/summary)

Get all orders (/orders)

✅ Day 2 — POST + Pydantic

Order creation with validation (/orders)

Field constraints using Field()

Error handling for invalid inputs

✅ Day 3 — Helper Functions + Filtering

find_item() → find item by ID

calculate_order_total() → pricing logic with delivery charges & discounts

filter_items_logic() → filter items

Filter endpoint (/items/filter)

✅ Day 4 — CRUD Operations

Add item (POST /items)

Update item (PUT /items/{item_id})

Delete item (DELETE /items/{item_id})

Duplicate check and business rules applied

✅ Day 5 — Multi-Step Workflow

Add to cart (/cart/add)

View cart (/cart)

Remove item (/cart/{item_id})

Checkout (/cart/checkout)

Complete flow: Cart → Checkout → Orders

✅ Day 6 — Advanced APIs

Search items (/items/search)

Sort items (/items/sort)

Pagination (/items/page)

Orders search, sort, pagination

Combined browsing (/items/browse)

🧠 Key Concepts Used

FastAPI Routing

Pydantic Models & Validation

Query Parameters

Helper Functions

CRUD Operations

Multi-step Workflows

Search, Sorting, Pagination

API Testing with Swagger UI

🗂 Project Structure
fastapi-grocery-delivery-app/
│
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
├── Q1_home.png
├── Q2_items.png
├── ...
└── Q20_browse.png
⚙️ How to Run the Project
1️⃣ Install dependencies
pip install -r requirements.txt
2️⃣ Run the FastAPI server
uvicorn main:app --reload
3️⃣ Open Swagger UI
http://127.0.0.1:8000/docs
📸 API Testing

All endpoints are tested using Swagger UI, and screenshots for all 20 tasks are included in the screenshots/ folder.

📦 Sample Functionalities

🛒 Add items to cart and checkout

📦 Place multiple orders

🔍 Search items by name/category

📊 Sort items by price/name/category

📄 Paginate results

🧠 Combined filtering + sorting + pagination

🎯 Project Outcome

This project demonstrates the ability to:

Design real-world REST APIs

Implement backend workflows

Apply clean coding practices

Handle validations and business logic

🙏 Acknowledgment

Grateful for the learning opportunity provided by Innomatics Research Labs.

🔗 Author

Yeshahswini M

GitHub: https://github.com/Yeshashwini-U

LinkedIn: https://www.linkedin.com/in/yeshashwini-u

🏷 Tags

#FastAPI #Python #BackendDevelopment #API #Project
