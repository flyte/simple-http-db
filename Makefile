.PHONY: build run up clean

build:
	docker build . --tag simple-http-db

run: build
	docker run -p 5000:5000 simple-http-db

up:
	docker-compose up

requirements.txt:
	pipenv lock --requirements > requirements.txt

clean:
	rm -f requirements.txt
