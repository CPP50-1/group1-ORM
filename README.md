# group1-ORM

## Local database

Copy `.env.example` to `.env` and replace the example password with a local value:

```sh
cp .env.example .env

```

Start PostgreSQL with:

```sh
docker compose up -d

```

### Testing the database

Once the container is running, you can verify the connection or interact with the database directly.

**Run a quick health check:**

```sh
docker exec -it python_local_pg pg_isready -U admin

```

**Open an interactive psql session:**

```sh
docker exec -it python_local_pg psql -U admin -d orm-db

```

*(Once inside, you can run `\dt` to list tables. Type `\q` to exit. Note: Replace `admin` and `orm-db` with your actual `.env` values if you modified them).*

**Connect from your host machine (if psql is installed locally):**

```sh
PGPASSWORD=admin psql -h localhost -p 5432 -U admin -d orm-db

```

### Stopping the database

Stop the database with:

```sh
docker compose down

```

`.env` is read automatically by Docker Compose and is ignored by Git. Do not commit it.