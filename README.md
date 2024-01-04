[![Python 3.12](https://img.shields.io/badge/python-3.12-green.svg)](https://www.python.org/downloads/release/python-3120/)
# trendyol-parser
## Описание
Данный сервис является парсером магазина [Trendyol](https://www.trendyol.com/). Является непосредственной частью системы
Markets-Bridge.

Его задачи:
1. Получает цели в виде ссылок на категории или товары магазина;
2. Парсит и валидирует товары;
3. Сохраняет их, обращаясь по API к [Markets-Bridge](https://github.com/qckzzi/markets-bridge-drf-app).

## Установка
### Конфигурация системы
Для функционирования системы необходимы:
- Запущенный instance [Markets-Bridge](https://github.com/qckzzi/markets-bridge-drf-app);
- [RabbitMQ server](https://www.rabbitmq.com/download.html);
- Python, поддерживаемой версии (разработка велась на 3.12.0).

### Установка проекта
Клонируем проект в необходимую директорию:
```shell
git clone git@github.com:qckzzi/trendyol-parser.git
```
```shell
cd trendyol-parser
```
Создадим виртуальное окружение:
```shell
python3 -m venv venv
```
(или любым другим удобным способом)

Активируем его:
```shell
. venv/bin/activate
```
Установим зависимости:

(для разработки)
```shell
pip install -r DEV_REQUIREMENTS.txt
```
(для деплоя)
```shell
pip install -r REQUIREMENTS.txt
```
В корневой директории проекта необходимо скопировать файл ".env.example", переименовать
его в ".env" и заполнить в соответствии с вашей системой.

Запуск сервиса:
```shell
python3 src/main.py
```
## Разработка

Для внесения изменений в кодовую базу необходимо инициализировать pre-commit git hook.
Это можно сделать командой в терминале, находясь в директории проекта:
```shell
pre-commit install
```
Это необходимо для поддержания 
единого кодстайла в проекте. При каждом коммите будет запущен форматировщик.