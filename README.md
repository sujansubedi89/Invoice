AI-Assisted Automated Email Delivery  Invoice Creation
# Invoice Management System

A full-stack Django application for creating, approving, and delivering branded PDF invoices, with AI-assisted form filling, role-based access control, and automated email delivery. The system is architected as a modular, white-label product suitable for resale and deployment across multiple client organizations.

---

## Table of Contents

- [Overview](#overview)
- [Demo and Live Deployment](#demo-and-live-deployment)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Demo Accounts](#demo-accounts)
- [White-Label Customization](#white-label-customization)
- [Switching AI Providers](#switching-ai-providers)
- [Roles and Permissions](#roles-and-permissions)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Invoice Management System enables a business to manage the full lifecycle of client invoicing — from creation and AI-assisted data entry, through a structured approval workflow, to branded PDF generation and automated email delivery. The system supports multiple user roles with distinct permissions and is designed to be deployed as a branded product for individual client companies without requiring source code modification.

---

## Demo and Live Deployment

**Video walkthrough:** [Loom Demo]( https://www.loom.com/share/9c392e9b2bea42149582ea2071bc6c09 )

A recorded walkthrough covering the core invoice workflow, role-based access, AI auto-fill, and PDF generation.

**Live deployment:** [https://your-app-name.onrender.com]( [https://your-app-name.onrender.com ](https://invoice-7qc7.onrender.com/))
 Demo user guest password :guest123
> **Note:** This deployment was previously hosted on Render's free tier. Free-tier services spin down after periods of inactivity and may take up to 60 seconds to respond to the first request after idling. The instance may also be suspended if Render's free-tier usage limits have been exceeded. For a guaranteed-available environment, refer to the local installation instructions below.

---

## Features

### Role-Based Access Control
Four distinct roles govern system access and capabilities: Administrator, Manager, Employee, and Guest. See [Roles and Permissions](#roles-and-permissions) for details.

### Invoice Lifecycle Management
Invoices progress through a defined workflow — Draft, Pending Approval, Approved, and Rejected — with a complete, timestamped audit trail of all status changes and approval comments.

### AI-Assisted Invoice Creation
Users may enter a plain-language description of work performed, and the system will automatically extract and populate structured invoice data, including client details, line items, currency, tax rate, due date, and payment details.

### PDF Invoice Generation
Approved invoices are rendered as professionally formatted PDF documents using ReportLab, including itemized line items, computed totals, payment instructions, and terms and conditions. Multi-currency support is included (NPR, USD, EUR, GBP, PKR, INR).

### Automated Email Delivery
Invoice PDFs are automatically delivered to clients via transactional email upon Guest creation or Manager/Administrator approval, with delivery failures handled gracefully and surfaced to the user.

### Role-Aware Dashboard
A summary dashboard presents invoice counts by status and a list of recent invoices, scoped appropriately to the authenticated user's role.

---

## Architecture

The application is organized into four independently maintained Django apps, each with a single area of responsibility:

| App | Responsibility |
|---|---|
| `users` | Authentication, user roles, and user management |
| `invoices` | Core invoice domain — models, CRUD operations, approval workflow, and PDF generation |
| `ai` | AI provider integration for invoice auto-fill, fully decoupled from any single vendor |
| `reports` | Dashboard statistics and the foundation for future analytics and reporting features |

This separation of concerns allows each domain to be developed, tested, and maintained independently, and provides a clear location for future functionality such as expanded reporting and analytics.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 6.0 |
| Database | PostgreSQL |
| PDF Generation | ReportLab |
| Email Delivery | Brevo (via django-anymail) |
| AI Provider | Groq or OpenRouter (configurable) |
| Static File Serving | WhiteNoise |
| Configuration Management | python-decouple |
| Deployment Target | Render |

---

## Project Structure

```
finalinvoice/
├── apps/
│   ├── users/              # Authentication and role management
│   ├── invoices/           # Core invoice domain and PDF generation
│   ├── ai/                 # AI provider integration
│   │   └── prompts/        # AI system prompts (editable without code changes)
│   └── reports/            # Dashboard statistics and reporting
├── config/                 # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/                 # Static assets (CSS, logo)
├── templates/               # Shared HTML templates
├── branding.py              # Centralized white-label configuration
├── manage.py
├── requirements.txt
├── .env.example              # Reference for required environment variables
└── README.md
```

---

## Prerequisites

The following must be installed before proceeding:

- Python 3.12 or later
- PostgreSQL 14 or later
- pip (Python package manager)
- A virtual environment tool (`venv`, included with Python)

---

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd finalinvoice
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\Activate.ps1

   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

1. **Create the environment file**

   ```bash
   cp .env.example .env
   ```

2. **Populate `.env` with the required values.** At minimum, the following must be set:

   | Variable | Description |
   |---|---|
   | `SECRET_KEY` | Django secret key |
   | `DEBUG` | `True` for local development, `False` in production |
   | `ALLOWED_HOSTS` | Comma-separated list of permitted hostnames |
   | `DATABASE_URL` or `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | Database connection details |
   | `AI_PROVIDER` | `groq` or `openrouter` |
   | `GROQ_API_KEY` / `GROQ_MODEL` | Required if using Groq |
   | `OPENROUTER_API_KEY` / `OPENROUTER_MODEL` | Required if using OpenRouter |
   | `BREVO_API_KEY` | Brevo transactional email API key |
   | `DEFAULT_FROM_EMAIL` | Sender address for outgoing email |

   Refer to `.env.example` for the complete list of supported configuration options, including white-label branding variables.

---

## Database Setup

1. **Create the PostgreSQL database**

   ```bash
   psql -U postgres -c "CREATE DATABASE invoice_db;"
   ```

2. **Apply migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Seed demo accounts (optional, recommended for development)**

   ```bash
   python manage.py seed_users
   ```

---

## Running the Application

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

---

## Demo Accounts

The `seed_users` management command provisions the following accounts for development and testing purposes:

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Administrator |
| `manager` | `manager123` | Manager |
| `employee` | `employee123` | Employee |
| `guest` | `guest123` | Guest |

> **Note:** These credentials are intended for local development only and must not be used in a production environment.

---

## White-Label Customization

The system is designed to be rebranded for individual client companies without modifying source code. All client-specific identity is centralized in `branding.py` and sourced from environment variables.

**To onboard a new client:**

1. Set the following variables in `.env`:

   ```ini
   BRAND_COMPANY_NAME=Client Company Pvt Ltd
   BRAND_COMPANY_TAGLINE=Client Tagline
   BRAND_LOGO_FILENAME=client_logo.jpg
   BRAND_COLOR_HEX=2563EB
   BRAND_INVOICE_PREFIX=INV
   ```

2. Place the client's logo file in the `static/` directory.

3. Configure database and email provider credentials for the client deployment.

4. Deploy. No source code changes are required.

Branding values are automatically applied across all generated PDFs, outgoing emails, and rendered templates via a shared Django context processor.

---

## Switching AI Providers

The AI auto-fill feature is decoupled from any single vendor and may be changed via a single environment variable:

```ini
# Default — fast and cost-effective
AI_PROVIDER=groq
GROQ_API_KEY=your-groq-key
GROQ_MODEL=llama-3.3-70b-versatile

# Alternative — broader model selection (GPT-4o, Claude, Gemini, etc.)
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=openai/gpt-4o-mini
```

The AI system prompt is maintained separately in `apps/ai/prompts/`, allowing prompt refinement without a code deployment.

---

## Roles and Permissions

| Role | Permissions |
|---|---|
| **Administrator** | Full system access, including user management, invoice approval/rejection, visibility into all invoices, and access to the Django administration panel |
| **Manager** | Approve or reject pending invoices; view all invoices across the organization |
| **Employee** | Create and submit invoices for approval; view only invoices they have created |
| **Guest** | Create an invoice that is automatically approved and emailed to the client immediately, bypassing the standard approval workflow |

---

## Deployment

The application is configured for deployment on [Render](https://render.com), but is compatible with any platform supporting Django and PostgreSQL.

**Render deployment steps:**

1. Provision a PostgreSQL database instance on Render and obtain its connection URL.
2. Create a new Web Service pointing to this repository.
3. Set all required environment variables (see `.env.example`) in the Render dashboard.
4. Configure the build command:

   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```

5. Configure the start command:

   ```bash
   gunicorn config.wsgi:application
   ```

6. Deploy the service.

> Ensure `DEBUG=False` and `ALLOWED_HOSTS` is correctly configured for the production domain before deploying.

---

## Contributing

1. Create a feature branch from `main`.
2. Make changes within the relevant app (`users`, `invoices`, `ai`, or `reports`), respecting the existing separation of concerns.
3. Ensure migrations are generated for any model changes.
4. Submit a pull request with a clear description of the change and its rationale.

---

## License

Proprietary. All rights reserved. This software is not licensed for redistribution without explicit written permission.
