# Running
See the root README for running using docker.

Run `uv run fastapi dev` from `/backend/`
- Replace `dev` with `run` for a production build

# Claude API
The main backend server includes an isolated Claude API adapter for the automated newsletter and other features.

Create a local environment file from `server/.env.example`:
```bash
cp server/.env.example server/.env
```

Set `ANTHROPIC_API_KEY` to the API key. The optional variables are:
- `CLAUDE_MODEL`, defaulting to `claude-sonnet-4-6`
- `CLAUDE_MAX_TOKENS`, defaulting to `1024`
- `CLAUDE_SYSTEM_PROMPT_PATH`, defaulting to `server/claude_interface/prompts/synthesis_system.txt`

For Docker, export the variables in your shell or place them in a root `.env` file before running `docker compose up`

# Type Checking
From `/backend` run `uv run mypy .`

# Testing
Run `uv run pytest` from `/backend` to run all backend tests.

Run `uv run pytest` from `/backend/<package>` to run all of that package's tests.
- This is equivalent to `uv run pytest <package>` from `/backend`

Pytest will find all files that match `test_*.py` or `*_test.py`, and then run all methods in those files that begin with the `test` prefix. Each package has a testing module to keep these tests in.
- For python/pytest namespace reasons, the testing modules have to have unique names (hence why I didn't name them all 'test')

# Formatting
Run `uv run ruff format` from `/backend` to prettify all python files.

Run `uv run ruff format` from `/backend/<package>` to format all of that package's python files.
- This is equivalent to `uv run ruff format <package>` from `/backend`

# Linting
Run `uv run ruff check`, which is called equivalently to formatting.

# Vercel
From the `/backend` repository

## Local Testing
```bash
vercel dev
```

## Deployment
```bash
vercel build
vercel deploy --prebuilt
```

# Cron
A single cron job is defined in `vercel.json`. This calls the `/cron` endpoint daily. This endpoint will run tasks as configured by the managers/administrators.

## Local Testing
Cron can be triggered manually by calling the `/cron` GET endpoint.

# Payments - Stripe

## Setup

Create API keys from the [Stripe Dashboard](https://dashboard.stripe.com) in the Developer section of the account settings.

- Populate backend keys: `STRIPE_API_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` in `backend/.env`.
- Populate frontend key: `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` in `frontend/.env`.

## Local Testing

1. Register the Stripe payment provider by running `uv run python seed.py stripe` from `/backend`. It accepts the name of any registered providers, so `mock stripe`, for example, seeds both.

2. `POST /payments/payments/donate` with an amount, which will return a `Payment` that stores its `paymentId`.

3. Choose Stripe on `/billing/selectProvider/<paymentId>`

4. Pay on `/billing/pay/<transactionId>`.

5. Observe the status on `/billing/confirmed/<transactionId>`.

## Test Cards

Stripe provides test cards with different statuses. Some examples are:

- `4242 4242 4242 4242` is a card that will succeed.
- `4000 0027 6000 3184` is a card that requires a 3DS2 challenge to succeed.
- `4000 0000 0000 0002` is a card that will decline.

Any future expiry data, CVC, and postcode are valid for testing with these cards.

There are many more cards available on the [Stripe Docs](https://docs.stripe.com/testing?testing-method=card-numbers#cards) for more extensive testing (different brands, etc).

# Auth Module Setup
To run the auth module locally, generate the following keys and add them to the .env file in the backend folder

## Generating Keys

**FERNET_KEY** : Used to encrypt TOTP secrets before storing in the database:
```bash
uv run --with cryptography python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
**SECRET_KEY** : RSA private key used for signing JWT tokens:
```bash
uv run python --with cryptography -c "from cryptography.hazmat.primitives.asymmetric import rsa; from cryptography.hazmat.primitives import serialization; key = rsa.generate_private_key(public_exponent=65537, key_size=2048); print(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()).decode())"
```