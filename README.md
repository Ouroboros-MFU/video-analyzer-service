# Video Analyzer Service

Cервис, который принимает видеофайл, проверяет наличие движения в кадре через OpenCV, сохраняет результат в PostgreSQL и отдаёт метрики в формате Prometheus.

## Инструкция по запуску.

### 1. Подготовить `.env.local` файл окружения.

В корне проекта создайте файл `.env.local` (если его ещё нет) со значениями для базы и приложения, например:

```env
# PostgreSQL
POSTGRES_DB=video_analyzer_db
POSTGRES_USER=video_analyzer_user
POSTGRES_PASSWORD=change_me
POSTGRES_PORT=5434              # внешний порт БД на хосте

# Внутренний порт БД в Docker (всегда 5432)
POSTGRES_INTERNAL_PORT=5432

# Строка подключения ДЛЯ ПРИЛОЖЕНИЯ (внутри Docker-сети)
DATABASE_URL=postgresql://video_analyzer_user:change_me@db:5432/video_analyzer_db

# API
APP_PORT=8000
APP_HOST=0.0.0.0

### 2. Собрать и запустить контейнеры.
Теперь необходимо выполнить команду «sudo docker compose --env-file .env.local up –d» чтобы запустить сборку и старт контейнера.
Для проверки, что контейнер собрался и запущен, необходимо выполнить команду «docker ps» и проверить, что контейнеры появились в списке.
Для проверки логов контейнера необходимо выполнить команду «docker logs идентификатор_контейнера».

API по умолчанию слушает на http://localhost:8000

### 3. Как проверить работу API
Откройте в браузере: http://localhost:8000/docs

Там будут доступны основные эндпоинты:

POST /analyze — принимает видеофайл и возвращает результат анализа;

GET /metrics — отдаёт метрики в формате Prometheus.

Через Swagger можно сразу:

Нажать на POST /analyze -> Нажать Try it out -> В поле file выбрать видео-файл -> Нажать Execute

В ответ должен прийти JSON с полями:

id
filename
has_motion
processing_time_seconds
error_message
created_at

Пример запроса через curl
Успешный запрос с видео
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/video.mp4"
Где /path/to/video.mp4 — путь до реального видео-файла на вашей машине.

Пример ответа:
{
  "filename": "1.MOV",
  "has_motion": true,
  "processing_time_seconds": 0.42779570699713076,
  "error_message": null,
  "id": 5,
  "created_at": "2025-11-17T18:29:58.718223Z"
}

Запрос с некорректным файлом
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/not_video.txt"

Пример ответа:
{
  "filename": "Dockerfile",
  "has_motion": false,
  "processing_time_seconds": 0.002008300001762109,
  "error_message": "Cannot open video file",
  "id": 4,
  "created_at": "2025-11-17T17:55:23.772888Z"
}

##Метрики Prometheus

Метрики доступны по адресу:

http://localhost:8000/metrics
Пример curl-запроса:
curl -X 'GET' \
  'http://localhost:8000/metrics' \
  -H 'accept: application/json'

Основные метрики:

videos_processed_total — сколько видео успешно обработано;
videos_processing_errors_total — сколько было ошибок;
videos_processing_time_seconds — гистограмма времени обработки видео.

