# nordigen-tasks
Take-Home Assignment


Environment varaibles for `.env` file:
```
POSTGRES_HOST=db
POSTGRES_DB=nordigen
POSTGRES_USER=dev
POSTGRES_PASSWORD=dev

LOGGING_LEVEL=DEBUG

DJANGO_SUPERUSER_NAME=admin
DJANGO_SUPERUSER_EMAIL=admin@localhost
DJANGO_SUPERUSER_PASSWORD=admin

REDIS_PASSWORD=redis

CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://:redis@redis:6379/0

NORDIGEN_ID=id
NORDIGEN_KEY=secretkey

SERVICE_ADDRESS=http://localhost:8000
```

Put `.env` file near docker-compose.yml.

Run `docker-compose -f docker-compose.yml up --build`

Visit: http://localhost:8000/

Admin: http://localhost:8000/admin/

Login with: DJANGO_SUPERUSER_NAME / DJANGO_SUPERUSER_PASSWORD values

`SERVICE_ADDRESS` is being used as a redirect address after access grant on the bank page.

Once you add an institution - background data fetch will start for accounts, balances and transactions.
Refresh the page after a while to see updates.