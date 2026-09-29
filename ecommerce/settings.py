"""
Django settings for the ecommerce project.
Simple e-commerce store — Task 1.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
# For a class project this is fine. For real deployment, load this from an
# environment variable instead.
SECRET_KEY = "django-insecure-change-this-key-for-production-abc123"

DEBUG = True

ALLOWED_HOSTS = ["*"]

# --- APPLICATIONS ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Makes the cart item count available on every page (navbar badge)
                "store.context_processors.cart_summary",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"

# --- DATABASE ---
# SQLite — zero setup, file-based, perfect for a mini project.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- STATIC & MEDIA FILES ---
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- AUTH REDIRECTS ---
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "product_list"
LOGOUT_REDIRECT_URL = "product_list"

# --- RAZORPAY (test mode) ---
# Get these from https://dashboard.razorpay.com/app/keys (make sure you're
# using the TEST mode keys — toggle is top-left on the Razorpay dashboard).
# Best practice is to set these as real environment variables rather than
# hardcoding them here, but a placeholder fallback is provided so the app
# doesn't crash if you forget — you'll just get a Razorpay auth error at checkout.
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "rzp_test_REPLACE_ME")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "REPLACE_ME_SECRET")

# When True (the default), checkout uses a simulated payment page instead of
# calling the real Razorpay API — no signup, no KYC/PAN, no API keys needed.
# Set the environment variable PAYMENT_MOCK_MODE=False once you have real
# Razorpay test keys to switch to the actual Razorpay Checkout widget.
PAYMENT_MOCK_MODE = os.environ.get("PAYMENT_MOCK_MODE", "True") == "True"
