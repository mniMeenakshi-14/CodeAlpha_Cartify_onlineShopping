# Cartify

A Django e-commerce site with product listings, search & category/price
filters, a session-based shopping cart, user registration/login, **real
Razorpay payment integration (test mode)**, and **product reviews &
ratings** — all backed by a SQLite database.

> **Why Razorpay and not Stripe?** Stripe has been invite-only for new
> Indian business accounts since May 2024, so it's not a practical option
> to sign up for right now. Razorpay is India's standard payment gateway
> (used widely by Indian companies) — a better fit for this project and a
> stronger line on an Indian resume.

> **About the "mock" payment mode:** Razorpay's own signup now asks for a
> PAN as part of account creation (RBI KYC rules), which you may not want
> to hand over just for a college project. So **by default this project
> runs in `PAYMENT_MOCK_MODE`** — a simulated payment page that mimics the
> real Razorpay flow (same views, same order/status logic, same
> success/failure paths) without ever calling Razorpay's API or needing an
> account. If you later do get real Razorpay test keys, set the
> environment variable `PAYMENT_MOCK_MODE=False` and the code automatically
> switches to the real Razorpay Checkout.js widget — no other changes needed.

## Features
- Product list & detail pages
- **Search** (by name/description) + **category filter** + **price range filter**
- Shopping cart (session-based — no login needed to browse/add to cart)
- User registration & login (Django's built-in auth)
- **Razorpay Checkout (test mode)** — real payment widget, signature-verified server-side before an order is marked paid
- **Product reviews & star ratings** — logged-in users can leave one review per product; average rating shown on listing & detail pages
- Order history page for logged-in users
- Django admin panel to manage products, categories, orders, and reviews

## Project structure
```
ecommerce_store/
├── manage.py
├── requirements.txt
├── ecommerce/          # project settings, urls
└── store/              # the app: models, views, templates, static
    ├── models.py        # Category, Product, Order, OrderItem, Review
    ├── cart.py           # session-based cart class
    ├── views.py           # includes Razorpay order creation & signature verification
    ├── urls.py
    ├── forms.py           # RegisterForm, CheckoutForm, ReviewForm
    ├── admin.py
    ├── templates/store/
    ├── templates/registration/
    ├── static/store/style.css
    └── fixtures/
        ├── sample_categories.json
        └── sample_products.json
```

## Setup (run these in order)

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies** (Django + Razorpay SDK):
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Get free Razorpay test API keys** — skip this entirely if
   you want to stay in mock mode (the default; see the note above):
   - Sign up at https://dashboard.razorpay.com/signup, complete the (now
     PAN-required) signup, and make sure you're in **Test Mode**
   - Go to **Settings → API Keys → Generate Test Key**
   - Copy your **Key ID** (`rzp_test_...`) and **Key Secret**
   - Set them as environment variables, and turn off mock mode:
     ```bash
     # macOS/Linux
     export RAZORPAY_KEY_ID="rzp_test_..."
     export RAZORPAY_KEY_SECRET="your_secret_here"
     export PAYMENT_MOCK_MODE="False"

     # Windows PowerShell
     $env:RAZORPAY_KEY_ID="rzp_test_..."
     $env:RAZORPAY_KEY_SECRET="your_secret_here"
     $env:PAYMENT_MOCK_MODE="False"
     ```

4. **Create the database tables**:
   ```bash
   python manage.py makemigrations store
   python manage.py migrate
   ```

5. **Load sample data**:
   ```bash
   python manage.py loaddata sample_categories
   python manage.py loaddata sample_products
   ```

6. **Create an admin account**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server**:
   ```bash
   python manage.py runserver
   ```

8. Open **http://127.0.0.1:8000/**
   - Admin panel: **http://127.0.0.1:8000/admin/**
   - Register a normal user at `/register/` to test cart, checkout, and reviews.

## Testing the payment flow (mock mode — default, no signup needed)
1. Add a product to your cart → go to checkout → fill shipping info → **Continue to Payment**
2. You'll land on a simulated payment page (clearly labeled "DEMO MODE") showing dummy card details
3. Click **Pay ₹...** to simulate a successful payment → order is marked **Paid**
4. Click **Simulate Failed Payment** to test the failure path → stock is restored, order is marked **Cancelled**

## Testing the real Razorpay payment flow (once you have API keys + `PAYMENT_MOCK_MODE=False`)
1. Same steps as above, but you'll see Razorpay's actual payment widget instead
2. Use Razorpay's official test values:
   - **Card:** `4111 1111 1111 1111`, any future expiry, any CVC
   - **UPI:** `success@razorpay` (simulates a successful payment)
3. On success, the server verifies Razorpay's cryptographic signature before marking the order **Paid** — this is the important security step (never trust the browser alone)

## How the pieces map to common "wow factor" resume points
| Feature | Where it lives |
|---|---|
| Search & filters | `product_list` view (`Q` lookups) + filter bar in `product_list.html` |
| Reviews & ratings | `Review` model, `submit_review` view, `average_rating()`/`review_count()` on `Product` |
| Razorpay payment (mock or real) | `razorpay_checkout`, `mock_payment_process`, `payment_verify`, `payment_failed` views in `store/views.py`; `mock_checkout.html` / `razorpay_checkout.html` |
| Product listings / cart / orders / auth | same as before — see `models.py`, `cart.py`, `views.py` |

## Notes for going further
- Add a **Razorpay webhook** (`payment.captured` event) as a second, server-to-server confirmation — right now verification relies on the browser successfully posting back to `payment_verify`, which is fine for a demo/resume project but not bulletproof if the user's connection drops mid-flow.
- Deploy to **Render** or **PythonAnywhere** and put the live link + a GitHub repo (with screenshots) in your resume — that matters more than any single feature.
