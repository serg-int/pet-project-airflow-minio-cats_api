# Pet Project: Airflow + MinIO + Cats API

Этот проект демонстрирует, как можно построить простой ETL-процесс с использованием Apache Airflow, MinIO и внешнего API для получения изображений котиков.

## Описание

В данном проекте реализован ETL-процесс, который:

- **Extract**: Получает данные (изображения котиков) из [The Cat API](https://thecatapi.com).
- **Transform**: Извлекает URL изображений из полученного JSON.
- **Load**: Скачивает изображения и загружает их в MinIO (S3-совместимое хранилище).

Вся логика ETL реализована в файле [`dags/tutorial_taskflow_api_etl.py`](./dags/tutorial_taskflow_api_etl.py) с использованием декораторов задач Airflow. Для стабильности задачи настроены повторы (retry) при неудачных попытках.

## Стек технологий

- **Apache Airflow** – оркестратор ETL-процессов.
- **MinIO** – S3-совместимое хранилище для загрузки изображений.
- **Docker Compose** – развёртывание среды с Airflow, PostgreSQL, Redis и MinIO.
- **The Cat API** – источник данных о котиках.

## Предварительные требования

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/serg-int/pet-project-airflow-minio-cats_api.git
cd pet-project-airflow-minio-cats_api
```

### 2. Настройка переменных окружения

Файл [`.env`](./.env) уже содержит минимальную настройку (например, `AIRFLOW_UID=50000`).

### 3. Запуск окружения

Запустите контейнеры с помощью Docker Compose:

```bash
docker-compose up -d
```

После успешного старта:

- Airflow Web UI будет доступен по адресу: [http://localhost:8080](http://localhost:8080) (Логин и пароль по умолчанию - airflow)
- Консоль MinIO – по адресу: [http://localhost:9001](http://localhost:9001) (Логин и пароль по умолчанию - minioadmin)

### 4. Настройка подключения к S3 (MinIO) в Airflow (Admin - Connections)

В MinIO нужно будет создать bucket, а в Airflow - connection к MinIO.
В файле [`airflow_connections.txt`](./airflow_connections.txt) указаны дополнительные параметры для подключения к MinIO. В поле `extra` необходимо указать JSON с информацией о регионе, имени бакета и URL конечной точки, например:

```json
{"region_name": "us-east-1", "bucket_name": "my-s3bucket", "endpoint_url": "http://airflow-s3:9000"}
```

## Использование

### 1. Запуск DAG

- Войдите в Airflow Web UI.
- Найдите DAG с тегом `cats` (название DAG — `my_cats_etl`).
- Запустите DAG вручную.

### 2. Логирование

- Логи выполнения задач будут доступны через интерфейс Airflow.
- В логах вы увидите сообщения об успешном извлечении, трансформации и загрузке изображений.

### 3. Проверка загрузки

- После выполнения DAG проверьте, что изображения успешно загружены в указанный бакет в MinIO.

## Дополнительные ресурсы

- [Статья на Хабре](https://habr.com/ru/articles/708276/) – источник вдохновения для данного решения.

## Примечания

- Проект предназначен для демонстрационных и обучающих целей.