.PHONY: run

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
