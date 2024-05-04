.PHONY: run

run:
	@python manage.py runserver

test:
	@python manage.py test

makemigrations:
	@python manage.py makemigrations accounts
	@python manage.py makemigrations manufacturer
	@python manage.py makemigrations prod 
	@python manage.py makemigrations order

import_and_seed:
	@python manage.py mfr_seed --mode refresh --nums 100
	@python manage.py prod_cate_import --csv Category_A_0206.csv
	@python manage.py prod_import --csv ItemBasic_A_0216.csv
	

migrate:
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

