# Foodgram, «Продуктовый помощник»

## О проекте
Данный проект является альтернативным вариантом реализации финального проекта курса бэкенд разработки на Python - Foodgram, «Продуктовый помощник» на Fastapi.

Foodgram - это сервис, который даёт возможность пользователям публиковать рецепты, подписываться на публикации других
пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список 
продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Для разработки проекта были выбраны такие паттерны проектирования, как __Репозиторий__ и __Сервисный слой__ (без особых проблем можно адаптировать управление проектом через Telegram-бота).

Проект запускается в четырех docker контейнерах:
- foodgram-db (PostgreSQL)
- foodgram-backend (FastAPI, SQLAlchemy)
- foodgram-frontend
- foodgram-nginx

Для создания списков покупок в формате __.pdf__ был использован модуль __wkhtmltopdf__, поэтому контейнер foodgram-backend получился увесистым.

Документация проекта в формате openapi доступна по адресу &_<project_domain_or_ip>:8000/docs_

## Полный стек проекта
- ![image](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)
- ![image](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
- ![image](https://img.shields.io/badge/SQLAlchemy-gray?style=for-the-badge&&logoColor=white)
- ![image](https://img.shields.io/badge/Alembic-black?style=for-the-badge&&logoColor=white)
- ![image](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=Pydantic&logoColor=white)
- ![image](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
- ![image](https://img.shields.io/badge/Uvicorn-31becf?style=for-the-badge&logoColor=white)
- ![image](https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white)
- ![image](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
- ![image](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)
- ![image](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)


## Запуск проекта
### Локальный запуск
1. Необходимо в директории backend создать файлы __.env__ (переменные окружения для запуска проекта) и __.env-test__ (для запуска тестов) в соответсвии с файлом __.env-example__.


2. Из директории __infra__ запускаем проект:
```py
docker compose up -d
```

3. Наполнение БД данными:
- базовые ингредиенты:
```
poe upload_ingredients
```
- базовые теги:
```
poe upload_ingredients
```
Данные добавляются из соответствующих .csv файлов, находящиеся в папке __data__. По аналогии с данными файлами можно создать файлы с собственными данными.

Также у администраторов есть возможность управлять тегами и ингредиентами через API (ручки под тегом "Для администраторов").

### Управление данными проекта
Манипулировать данными проекта можно посредством инструментов администрирования базами данных. Например, при помощи DBeaver.