.PHONY: dev dev-clean migrate migrate-down psql db-wait

DATABASE_URL ?= postgres://diamond:diamond@localhost:5433/diamond?sslmode=disable

# Bring up local stack and initialize DB schema.
dev:
	docker compose up -d --build db mlb-mock api ingest web
	make db-wait
	docker compose run --rm db-init
	@echo "dev stack ready: db(5433), mlb-mock(8090), api(18000), web(5174)"

# Tear down local stack and remove DB volume.
dev-clean:
	docker compose down -v --remove-orphans

# Wait until Postgres answers.
db-wait:
	@echo "waiting for postgres..."
	@for i in $$(seq 1 30); do \
		docker exec diamond-db pg_isready -U diamond -d diamond -p 5432 >/dev/null 2>&1 && exit 0; \
		sleep 1; \
	done; \
	echo "postgres did not become ready"; exit 1

migrate:
	@if command -v migrate >/dev/null 2>&1; then \
		migrate -database "$(DATABASE_URL)" -path apps/api/migrations up; \
	else \
		docker run --rm --network host -v "$(PWD)/apps/api/migrations:/migrations:ro" migrate/migrate:v4.18.3 \
			-path=/migrations -database "$(DATABASE_URL)" up; \
	fi

migrate-down:
	@if command -v migrate >/dev/null 2>&1; then \
		migrate -database "$(DATABASE_URL)" -path apps/api/migrations down -all; \
	else \
		docker run --rm --network host -v "$(PWD)/apps/api/migrations:/migrations:ro" migrate/migrate:v4.18.3 \
			-path=/migrations -database "$(DATABASE_URL)" down -all; \
	fi

psql:
	docker exec -it diamond-db psql -U diamond -d diamond
