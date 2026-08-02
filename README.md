# Development
## uv
Install uv with `pip install uv`

# Install Docker
For WSL2
```bash
sudo apt-get install docker.io
sudo apt-get install docker-compose-v2 # Note the v2!
```

# Launch our application
`sudo docker compose up --build -d`
- This will incorporate any changes since you last launched.

# Inspect the Database
`sudo docker container exec -it bentley-sem-1-02-db-1 psql -d database -U username -W`
And enter the password "password"

# Setting up Supabase
1. Create a project at [supabase.com](https://supabase.com)
2. Go to Project Settings → Database → Connection Pooling
3. Copy the **Session Pooler** connection string (not the direct connection — 
   the direct connection requires IPv6 and often fails, especially on Windows)
4. Add it to your `.env` file:
    SUPABASE_DATABASE_URL=postgresql://postgres.your-project-ref:your-password@aws-0-region.pooler.supabase.com:5432/postgres
5. Set `LOCAL_DEPLOYMENT=False` in `.env` to connect to Supabase instead of a local database

See Supabase's [connection docs](https://supabase.com/docs/guides/database/connecting-to-postgres) for more detail.
