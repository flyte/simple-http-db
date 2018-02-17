.PHONY: build run up clean

requirements.txt:
	pipenv lock --requirements > requirements.txt

build: requirements.txt
	docker build . --tag simple-http-db

run: build
	docker run -p 5000:5000 simple-http-db

up:
	docker-compose up

clean:
	rm -f requirements.txt
