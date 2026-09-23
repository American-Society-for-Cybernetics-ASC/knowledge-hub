# Supabase
Create a project at [supabase.com](https://supabase.com)

# Vercel
Create a project at [vercel.com](https://vercel.com).

## Environment Variables
In your vercel project, navigate to `/settings/environments/production`. Ensure you have the following environment variables set:

### DATABASE_URL
1. Go [here](https://supabase.com/dashboard/project/_?showConnect=true&method=transaction).
2. Select Direct (Connection string), Method=Transaction Pooler and type=URI
3. Copy the **Session Pooler** connection string (not the direct connection — 
   the direct connection requires IPv6 and often fails, especially on Windows)
    - Replace [YOUR-PASSWORD] with the database password. If you do not know the database password, you will have to reset it.
4. Add a **secret** environment variable `DATABASE_URL` set to that connection string.

See Supabase's [connection docs](https://supabase.com/docs/guides/database/connecting-to-postgres) for more detail.

### SECRET_KEY and FERNET_KEY
See [here](https://pip.pypa.io/en/stable/installation/) for how to install pip.

If you have pip installed, run the following to generate a pair of keys
```bash
pip install uv
uv run generate_keys.py
```

Add **secret** environment variables SECRET_KEY and FERNET_KEY appropriately.
- SECRET_KEY does not include the "-----BEGIN RSA PRIVATE KEY-----" or "-----END RSA PRIVATE KEY-----" sections.

### NEXT_PUBLIC_API_URL
Add a **config** variable NEXT_PUBLIC_API_URL, with its value set to `/api`.

# Production Deploy
Preview with 
```bash
vercel deploy --archive=tgz
```

Deploy with
```bash
vercel deploy --prod --archive=tgz
```

# FAQ
## Vercel Services are in beta
This feature simplifies our deployment massively, and solves a domain issue very neatly. However, if the feature breaks, the same setup can be recreated with a [proxy project](https://vercel.com/kb/guide/how-can-i-serve-multiple-projects-under-a-single-domain#with-a-proxy-project).