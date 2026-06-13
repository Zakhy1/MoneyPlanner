class ApplicationError(Exception):
    """Базовое исключение для приложения."""

    pass


class ObjectDoesNotExistsError(ApplicationError):
    """Базовое исключение для ситуаций, когда объект не найден."""

    name = "Object"


class ValidationError(ApplicationError):
    def __init__(self, reason: str = "Validation Error"):
        self.reason = reason


class OwnerPermissionError(ApplicationError):
    """Возникает, когда пользователь пытается взаимодействовать не со своими объектами"""

    pass


class CategoryDoesNotExistsError(ObjectDoesNotExistsError):
    """Возникает, когда искомая категория не найдена."""

    name = "Category"


class CategoryDirectionMismatchError(ApplicationError):
    """Возникает, когда direction родительской и дочерней категории различаются."""

    pass


class CategoryRecursionParentError(ApplicationError):
    """Возникает, когда категория ссылается на саму себя в parent_id"""

    pass


class ChildCategoryExistsError(ApplicationError):
    """Возникает, когда происходит попытка удаления категории, у которой есть потомки"""

    pass


class TransactionExistsError(ApplicationError):
    """
    Возникает, когда происходит попытка удаления категории у которой есть транзакции.
    Транзакции должны быть перемещены в другую категорию
    """

    pass


class CategoryNameDoesNotUniqueError(ApplicationError):
    """
    Возникает, когда происходит попытка создания категории с не уникальным именем
    """

    pass


class AcccountDoesNotExistsError(ObjectDoesNotExistsError):
    """Возникает, когда искомая категория не найдена."""

    name = "Account"
