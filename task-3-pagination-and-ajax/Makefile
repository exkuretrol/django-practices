.PHONY: run

init:
	@poetry install --no-root
	@poetry shell
	@npm install
	@django-admin startproject django_project .
	@mkdir -p static/src
	@echo "@tailwind base;\n@tailwind components;\n@tailwind utilities;" > static/src/input.css

run:
	@npm run tailwind	
	@python manage.py runserver

test:
	@python manage.py test

tailwind:
	@npm run tailwind-watch

migrate:
	@python manage.py makemigrations
	@python manage.py migrate

collectstatic:
	@python manage.py collectstatic

shell:
	@python manage.py shell
