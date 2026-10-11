# Setup
## Install Docker
For WSL2
```bash
sudo apt-get install docker.io
sudo apt-get install docker-compose-v2 # Note the v2!
```

## Set environment variables
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
Then, update `backend/.env` according to the comments in that file.

## Launch our application
```bash
sudo docker compose up --build -d
```
- This will incorporate any changes since you last launched.

# Troubleshooting
## Inspect the Backend
```bash
sudo docker container logs bentley-sem-1-02-server-1
```
Will print out the backend server logs

## Inspect the Database
```bash
sudo docker container exec -it bentley-sem-1-02-db-1 psql -d database -U username -W
```
And enter the password "password"

# Payments - Stripe
## Setup

Create API keys from the [Stripe Dashboard](https://dashboard.stripe.com) in the Developer section of the account settings.

- Populate backend keys: `STRIPE_API_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` in `backend/.env`.
- Populate frontend key: `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` in `frontend/.env`.

## Test Cards

Stripe provides test cards with different statuses. Some examples are:

- `4242 4242 4242 4242` is a card that will succeed.
- `4000 0027 6000 3184` is a card that requires a 3DS2 challenge to succeed.
- `4000 0000 0000 0002` is a card that will decline.

Any future expiry data, CVC, and postcode are valid for testing with these cards.

There are many more cards available on the [Stripe Docs](https://docs.stripe.com/testing?testing-method=card-numbers#cards) for more extensive testing (different brands, etc).
