class Error(Exception):
    """Базовый класс для исключений в этом модуле."""

    pass


class ApiReqestException(Error):
    """Ну удалось получить ответ от API."""

    ...
