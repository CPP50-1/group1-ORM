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

Stop it with:

```sh
docker compose down
```

`.env` is read automatically by Docker Compose and is ignored by Git. Do not commit it.

## GitHub Actions secrets

Add these repository secrets under **Settings > Secrets and variables > Actions > New repository secret**:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

GitHub Actions does not automatically pass repository secrets into Docker Compose. Expose them on the workflow step that runs Compose:

```yaml
- name: Start database
	run: docker compose up -d
	env:
		POSTGRES_USER: ${{ secrets.POSTGRES_USER }}
		POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
		POSTGRES_DB: ${{ secrets.POSTGRES_DB }}
```

Use `${{ secrets.NAME }}` only in workflow files. For pull requests from forks, GitHub does not provide repository secrets, so steps requiring these secrets should be skipped or use a separate non-secret test database configuration.