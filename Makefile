.PHONY: serve web mobile install init-db

serve:
	cd apps/api && uv run recall serve

web:
	npm --workspace @recall/web run dev

mobile:
	npm --workspace @recall/mobile run start

install:
	cd apps/api && uv sync
	npm install

init-db:
	cd apps/api && uv run recall init-db
