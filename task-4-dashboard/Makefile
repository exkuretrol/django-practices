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

prod_refresh:
	@python manage.py prod_seed --mode refresh --nums 1000

prod_empty:
	@python manage.py prod_seed --mode empty

clean:
	@find . -type f -name ".DS_Store" -execdir rm -rf {} \;
	@find . -type d -name "migrations" -execdir rm -rf {} \;
	@find . -type d -name "__pycache__" -execdir rm -rf {} \;
	@find . -type f -name "db.sqlite3" -execdir rm -rf {} \;
	@find ./media -type f -execdir rm -rf {} \;
