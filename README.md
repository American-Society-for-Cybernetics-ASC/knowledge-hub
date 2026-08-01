# Development
## uv
Install uv with `pip install uv`

## Install Docker
For WSL2
```bash
sudo apt-get install docker.io
sudo apt-get install docker-compose-v2 # Note the v2!
```

## Launch our application
`sudo docker compose up --build -d`
- This will incorporate any changes since you last launched.

## Inspect the Database
`sudo docker container exec -it bentley-sem-1-02-db-1 psql -d database -U username -W`
And enter the password "password"
