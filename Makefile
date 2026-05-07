.PHONY: dev migrate migrate-down

dev:
	@echo "not yet implemented"

migrate:
	@test -n "$$DATABASE_URL" || { echo "DATABASE_URL is required"; exit 1; }
	migrate -database "$$DATABASE_URL" -path apps/api/migrations up

migrate-down:
	@test -n "$$DATABASE_URL" || { echo "DATABASE_URL is required"; exit 1; }
	migrate -database "$$DATABASE_URL" -path apps/api/migrations down -all
