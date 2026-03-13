# VideoTranscoder 🎥

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.129.0-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791.svg)](https://www.postgresql.org/)
[![Celery](https://img.shields.io/badge/Celery-5.4.0-green.svg)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED.svg)](https://www.docker.com/)
[![codecov](https://codecov.io/gh/nikitaorlovski/videotranscoder/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/videotranscoder)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Современный сервис для транскодирования видео с поддержкой различных форматов и разрешений. Построен на стеке FastAPI + Celery + FFmpeg с асинхронной обработкой задач.

## ✨ Особенности

- 🚀 **Асинхронная архитектура** - FastAPI + async/await для максимальной производительности
- 🔄 **Фоновые задачи** - Celery для распределенной обработки видео
- 🎬 **Множество форматов** - Поддержка MP4, WebM, MOV, MKV, AVI
- 📱 **Адаптация разрешений** - Конвертация в 480p с сохранением пропорций
- 🖼️ **Генерация превью** - Автоматическое создание миниатюр из видео
- 🔐 **JWT аутентификация** - Безопасный доступ с RS256 подписью
- 🐳 **Docker ready** - Полная контейнеризация всех сервисов
- 📊 **Масштабируемость** - Горизонтальное масштабирование через Celery workers


### Компоненты системы

- **FastAPI приложение** - обрабатывает HTTP запросы, аутентификацию и валидацию
- **PostgreSQL** - хранение метаданных пользователей и видео
- **Redis** - брокер сообщений для Celery и кэширование
- **Celery workers** - асинхронная обработка видео (конвертация, генерация превью)
- **FFmpeg** - непосредственное транскодирование видеофайлов

## 🛠️ Технологический стек

### Backend
- **Framework**: FastAPI
- **База данных**: PostgreSQL + asyncpg + SQLAlchemy 2.0
- **Очереди задач**: Celery + Redis
- **Аутентификация**: JWT (RS256) + bcrypt
- **Миграции**: Alembic

### Обработка видео
- **FFmpeg** - асинхронные subprocess вызовы
- **Поддерживаемые форматы**: MP4, WebM, MOV, MKV, AVI
- **Кодеки**: H.264, VP9, MPEG4, AAC, MP3, Opus

### Инфраструктура
- **Контейнеризация**: Docker + Docker Compose
- **Web сервер**: Uvicorn
- **Мониторинг**: Celery Flower (планируется)

### Тестирование
- **Pytest** + pytest-asyncio
- **HTTPX** для асинхронного тестирования API
- **pytest-cov** для анализа покрытия
- **pytest-mock** для изоляции тестов

## 📋 Предварительные требования

- Python 3.12+
- Docker и Docker Compose (рекомендуется)
- PostgreSQL 17+
- Redis 8+
- FFmpeg (для локальной разработки)

## 🚀 Быстрый старт

### Вариант 1: Локальная разработка

#### 1. Клонировать репозиторий
```bash
git clone https://github.com/yourusername/videotranscoder.git
cd videotranscoder
```
#### 2. Создать виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```
#### 3. Установить зависимости через Poetry
```bash
pip install poetry
poetry install
```
#### 4. Настроить переменные окружения
```bash
cp .env.example .env
```
###### Отредактируйте .env файл под свои параметры
#### 5. Сгенерировать RSA ключи для JWT
```bash
mkdir -p certs
openssl genrsa -out certs/private.pem 2048
openssl rsa -in certs/private.pem -pubout -out certs/public.pem
```
#### 6. Запустить миграции базы данных
```bash
alembic upgrade head
```
#### 7. Запустить приложение
Терминал 1: FastAPI приложение

```bash
uvicorn main:app --reload
```
Терминал 2: Celery worker

```bash
celery -A app.celery.celery_app:app worker -l info
```
#### Вариант 2: Запуск через Docker Compose (рекомендуется)
```bash
docker-compose up --build
```
После запуска сервисы будут доступны:

FastAPI приложение: http://localhost:8000
Документация API (Swagger): http://localhost:8000/docs
Альтернативная документация (ReDoc): http://localhost:8000/redoc
pgAdmin: http://localhost:8080 (admin@admin.com / admin)