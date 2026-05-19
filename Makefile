KAFKA_TEST_NAME := kafka-test
ADMIN_TEST_NAME := admin-test
ADMIN_PORT := 5050
NOTIFIER_TEST_NAME := notifier-test
NOTIFIER_PORT := 5500
FRONTEND_TEST_NAME := frontend-test
FRONTEND_PORT := 5000
BACKEND_TEST_NAME := backend-test
BACKEND_PORT := 3000
DATABASE_TEST_NAME := database-test
DATABASE_PORT := 4000

build-doc:
	pandoc --pdf-engine=xelatex README.md -V colorlinks=true -V linkcolor=blue -o felhohf_1.pdf

admin-build:
	docker build -t ${ADMIN_TEST_NAME} admin/

admin-shell: admin-build
	docker run --rm -ti --entrypoint sh -p ${ADMIN_PORT}:5000 ${ADMIN_TEST_NAME}

admin-run: admin-build
	docker run --rm -p ${ADMIN_PORT}:5000 ${ADMIN_TEST_NAME}

admin-clean:
	docker image rm ${ADMIN_TEST_NAME}

notifier-build:
	docker build -t ${NOTIFIER_TEST_NAME} notifier/

notifier-shell: notifier-build
	docker run --rm -ti --entrypoint sh -p ${NOTIFIER_PORT}:5000 ${NOTIFIER_TEST_NAME}

notifier-run: notifier-build
	docker run --rm -p ${NOTIFIER_PORT}:5000 ${NOTIFIER_TEST_NAME}

notifier-clean:
	docker image rm ${NOTIFIER_TEST_NAME}

backend-build:
	docker build -t ${BACKEND_TEST_NAME} backend/

backend-shell: backend-build
	docker run --rm -ti --entrypoint sh -p ${BACKEND_PORT}:5000 ${BACKEND_TEST_NAME}

backend-run: backend-build
	docker run --rm -p ${BACKEND_PORT}:5000 ${BACKEND_TEST_NAME}

backend-clean:
	docker image rm ${BACKEND_TEST_NAME}

frontend-build:
	docker build -t ${FRONTEND_TEST_NAME} frontend/

frontend-shell: frontend-build
	docker run --rm -ti --entrypoint sh -p ${FRONTEND_PORT}:5000 ${FRONTEND_TEST_NAME}

frontend-run: frontend-build
	docker run --rm -p ${FRONTEND_PORT}:5000 ${FRONTEND_TEST_NAME}

frontend-clean:
	docker image rm ${FRONTEND_TEST_NAME}

database-build:
	docker build -t ${DATABASE_TEST_NAME} db_handler/

database-shell: database-build
	docker run --rm -ti --entrypoint sh -p ${DATABASE_PORT}:5000 ${DATABASE_TEST_NAME}

database-run: database-build
	docker run --rm -p ${DATABASE_PORT}:5000 ${DATABASE_TEST_NAME}

database-clean:
	docker image rm ${DATABASE_TEST_NAME}

kafka-build:
	docker build -t ${KAFKA_TEST_NAME} kafka/

kafka-shell: kafka-build
	docker run --rm -ti --entrypoint sh ${KAFKA_TEST_NAME}

kafka-run: kafka-build
	docker run --rm ${KAFKA_TEST_NAME}

kafka-clean:
	docker image rm ${KAFKA_TEST_NAME}

clean: admin-clean notifier-clean backend-clean frontend-clean database-clean kafka-clean

compose: admin-build notifier-build database-build frontend-build backend-build kafka-build
	cd dev && docker compose up