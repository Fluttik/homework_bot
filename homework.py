import logging
import os
import sys
import time

import requests
import telegram

from dotenv import load_dotenv
from http import HTTPStatus

from exceptions import ApiReqestException

load_dotenv()
PRACTICUM_TOKEN = os.getenv('TOKEN_PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TOKEN_TELEGRAM')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='homework_check_bot.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s -  %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)


def check_tokens():
    """Проверяет доступность переменных окружения.
    которые необходимы для работы программы
    """
    return all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PRACTICUM_TOKEN])


def send_message(bot, message):
    """Отправка сообщения в телеграмм."""
    try:
        logger.debug('Начата попытка отправки сообщения')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Сообщение отправленно')
    except telegram.TelegramError:
        logger.error('Сообщение не отправлненно')


def get_api_answer(timestamp):
    """Получает ответ от API Яндекс.Домашки."""
    payload = {'from_date': timestamp}
    try:
        homework = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        status_code = homework.status_code
        if status_code != HTTPStatus.OK:
            raise requests.Timeout(
                f'API Яндекс.Домашка недоступен статус: {status_code}')
    except requests.exceptions.RequestException as error_request:
        raise ApiReqestException(f'API недоступен: {error_request}')
    return homework.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logger.debug('Проверка response начата')
    if not isinstance(response, dict):
        raise TypeError('response не является dict')
    elif 'homeworks' not in response:
        raise KeyError("В ответе API отсутвует ключ 'homeworks'")
    elif 'current_date' not in response:
        raise KeyError("В ответе API отсутвует ключ 'current_date'")
    elif not isinstance(response['homeworks'], list):
        raise TypeError('Неверный тип данных у homeworks')
    return response.get('homeworks')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе.
    статус этой работы
    """
    logger.debug('Начато извлечение информации')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status is None:
        raise NameError
    if homework_status not in HOMEWORK_VERDICTS:
        raise NameError
    if homework_name is None:
        raise NameError
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствует токен(ы) окружения')
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_error = ''
    previous_homework_status = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response.get('current_date')
            homework = check_response(response)
            if homework:
                actual_homework = homework[0]
                homework_status = parse_status(actual_homework)
                print(homework_status)
                if homework_status != previous_homework_status:
                    send_message(bot, homework_status)
                    previous_homework_status = homework_status
            else:
                homework_status = 'Нет нового статуса домашки'
                logger.debug('Нет новых статусов')
                if homework_status != previous_homework_status:
                    send_message(bot, homework_status)
                    previous_homework_status = homework_status
            #     send_message(bot, f'Новый статус домашки - {homework_status}')
            # else:
            #     send_message(bot, 'Нет нового статуса домашки')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != last_error:
                last_error = error
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
