# Configuration Guide

This document outlines the environment variables and settings available to configure the Internship Management and Assessment System (IMS).

---

## 1. Core Settings

| Environment Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key for cryptographic signing | `django-insecure-ims-...` |
| `DEBUG` | Enable/disable Django debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed host headers | `*` |

---

## 2. Database Configuration

By default, the application uses **SQLite** for zero-setup local execution. To switch to **PostgreSQL** in production or staging, configure the following:

| Environment Variable | Description | Default |
|---|---|---|
| `USE_POSTGRES` | Set to `True` to enable PostgreSQL | `False` |
| `DB_NAME` | Name of the PostgreSQL database | `ims_db` |
| `DB_USER` | PostgreSQL user | `ims_user` |
| `DB_PASSWORD` | PostgreSQL user password | `ims_password` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |

---

## 3. Email Settings (SMTP)

By default, verification automation notifications are printed to the **django console backend**. For real SMTP delivery, configure the following:

| Environment Variable | Description | Default |
|---|---|---|
| `USE_SMTP_EMAIL` | Set to `True` to enable SMTP delivery | `False` |
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USE_TLS` | Enable TLS encryption | `True` |
| `SMTP_USER` | SMTP username/email address | *(Empty string)* |
| `SMTP_PASSWORD` | SMTP password/app password | *(Empty string)* |
| `SMTP_FROM_EMAIL` | Sender email address for automated mail | *(Defaults to `SMTP_USER`)* |

---
