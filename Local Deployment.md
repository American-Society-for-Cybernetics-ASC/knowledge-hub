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
Then, update `backend/.env`

## Launch our application
```bash
sudo docker compose up --build -d
```
- This will incorporate any changes since you last launched.

# Error checking
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
