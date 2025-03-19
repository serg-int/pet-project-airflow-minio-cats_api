"""
https://habr.com/ru/articles/708276/ - статья с хабра
"""
import pendulum
import requests
import json
import time

from typing import List
from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

@dag(
    schedule=None,  # DAG запускается вручную (нет расписания)
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),  # Начальная дата DAG-а
    catchup=False,  # Отключаем выполнение старых задач
    tags=["cats"],  # Тег для фильтрации DAG-ов в UI
    description="DAG для обработки данных о котиках.",  # Описание DAG-а
)
def my_cats_etl():
    """
    Простой ETL-процесс для получения картинок котиков с API,
    трансформации данных и загрузки изображений в MinIO.
    """

    @task(retries=3, retry_delay=pendulum.duration(seconds=5))  # Повторяет задачу 3 раза с паузой 5 сек
    def extract() -> List[dict]:
        """
        Запрашивает данные о 10 котиках из API.
        """
        response = requests.get("https://api.thecatapi.com/v1/images/search?limit=10")
        response.raise_for_status()  # Проверяем, не вернул ли API ошибку
        print("✅ Data extracted successfully")  # Логируем успешное выполнение
        return response.json()  # Возвращаем JSON с данными о котиках

    @task()
    def transform(data: List[dict]) -> List[str]:
        """
        Преобразует JSON-ответ в список URL изображений.
        """
        urls = [i['url'] for i in data]
        print(f"✅ Transformed data: {urls}")  # Логируем список URL
        return urls

    @task()
    def load_to_minio(data: List[str]):
        """
        Скачивает изображения котиков и загружает их в MinIO.
        Если скачивание не удалось, делает до 3 попыток.
        """
        hook = S3Hook(aws_conn_id="S3_ETL_CONN")
        extra = hook.get_connection(hook.aws_conn_id).get_extra()
        bucket_name = json.loads(extra)['bucket_name']

        for url in data:
            for attempt in range(3):  # Делаем 3 попытки запроса
                try:
                    response = requests.get(url, timeout=5)  # Запрос с таймаутом 5 секунд
                    response.raise_for_status()  # Проверяем статус ответа

                    file_name = url.split('/')[-1]  # Получаем имя файла из URL
                    hook.load_bytes(response.content, key=file_name, bucket_name=bucket_name)  # Загружаем в MinIO
                    print(f"✅ Uploaded {file_name} to {bucket_name}")  # Логируем успешную загрузку
                    break  # Если запрос успешен, выходим из цикла
                except requests.exceptions.RequestException as e:
                    print(f"⚠️ Attempt {attempt+1}: Failed to fetch {url} - {e}")  # Логируем ошибку
                    time.sleep(2)  # Ждём 2 секунды перед повторной попыткой
            else:
                print(f"❌ Failed to fetch {url} after 3 attempts")  # Логируем окончательную неудачу

    # Определяем порядок выполнения задач
    extracted_data = extract()
    transformed_data = transform(extracted_data)
    load_to_minio(transformed_data)

# Запускаем DAG
my_cats_etl()
