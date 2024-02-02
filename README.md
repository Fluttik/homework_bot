# Телеграм бот для проверки статуса домашей работы
##### Данный бот отправляет запрос на API яндекс практикума и получает ответ, после чего обрабатывает его, записывает лог и отправляет пользователю статус.


## Библиотеки 
- python-telegram-bot


And of course Dillinger itself is open source with a [public repository][dill]
 on GitHub.
Автор: Николай Королёв
### Инструкция по установке
##### Клонируем репозиторий на компьютер:

```bash
1) git@github.com:Fluttik/homework_bot.git
2) cd homework_bot
```

##### Cоздаем и активируем виртуальное окружение:
##### Windows

```bash
python -m venv venv 
```
```bash
source venv/Scripts/activate 
```

 ##### Linux
```bash
python3 -m venv venv 
```

```bash
source venv/bin/activate # Linux
```
##### Устанавливаем зависимости проекта:


```
pip install -r requirements.txt
```
#### Создание .env файла
##### В данном файле необходимо хранить следующие токены:
 - PRACTICUM_TOKEN (токен для доступа к API яндекса)
 - TELEGRAM_TOKEN (токен вашего телеграм бота)
 - TELEGRAM_CHAT_ID (id чата с пользователем)

#### Запуск бота
```
python homework.py
```
homework.py
Автор: Николай Королёв
