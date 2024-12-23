# Foodgram, «Продуктовый помощник»

## О проекте
Foodgram - это сервис, который даёт возможность пользователям публиковать рецепты, подписываться на публикации других
пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список 
продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
## Стек проекта
- ![image](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)
- ![image](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
- ![image](https://img.shields.io/badge/SQLAlchemy-gray?style=for-the-badge&&logoColor=white)
- ![image](https://img.shields.io/badge/Alembic-black?style=for-the-badge&&logoColor=white)
- ![image](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=Pydantic&logoColor=white)
- ![image](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
- ![image](https://img.shields.io/badge/Uvicorn-31becf?style=for-the-badge&logoColor=white)
- ![image](https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white)

## Запуск проекта
### Локальный запуск
1. Необходимо в директории backend создать файлы __.env__ (переменные окружения для запуска проекта) и 
__.env-test__ (для запуска тестов) в соответсвии с файлом .env-example

2. Из директории infra запускаем проект:
```py
docker compose up -d
```
3. Наполнение БД данными:
- базовые ингредиенты при помощи команды
```
poe upload_ingredients
```
- базовые теги при помощи команды
```
poe upload_ingredients
```
Данные добавляются из файлов .csv, находящиеся в папке data, поэтому по аналогии с данными файлами можно создать
подобные файлы с другими данными
