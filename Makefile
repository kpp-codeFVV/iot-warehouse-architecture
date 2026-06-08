.PHONY: install test compile gateway inventory alert sample abnormal low-stock docker-up

install:
	python -m venv .venv
	.venv/Scripts/python -m pip install -r requirements.txt

test:
	.venv/Scripts/python -m pytest tests -q

compile:
	.venv/Scripts/python -m py_compile libs/iot_core.py apps/device-gateway/main.py apps/inventory-service/main.py apps/alert-service/main.py scripts/data-gen/send_sample.py scripts/load-test/local_load.py scripts/fault-injection/cloud_outage_demo.py

gateway:
	.venv/Scripts/python -m uvicorn main:app --app-dir apps/device-gateway --port 8001

inventory:
	.venv/Scripts/python -m uvicorn main:app --app-dir apps/inventory-service --port 8002

alert:
	.venv/Scripts/python -m uvicorn main:app --app-dir apps/alert-service --port 8003

sample:
	.venv/Scripts/python scripts/data-gen/send_sample.py

abnormal:
	.venv/Scripts/python scripts/data-gen/send_sample.py --abnormal

low-stock:
	.venv/Scripts/python scripts/data-gen/send_sample.py --low-stock

docker-up:
	docker compose up
