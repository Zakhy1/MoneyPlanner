class ApplicationError(Exception):
    """Базовое исключение для приложения."""

    pass


class ObjectDoesNotExistsError(ApplicationError):
    """Базовое исключение для ситуаций, когда объект не найден."""

    pass


class OwnerPermissionError(ApplicationError):
    """Возникает, когда пользователь пытается взаимодействовать не со своими объектами"""

    pass


class CategoryDoesNotExistsError(ObjectDoesNotExistsError):
    """Возникает, когда искомая категория не найдена."""

    pass


class ParentCategoryDoesNotExistsError(CategoryDoesNotExistsError):
    """Возникает, когда искомая категория не найдена."""

    pass


class CategoryDirectionMismatchError(ApplicationError):
    """Возникает, когда direction родительской и дочерней категории различаются."""

    pass


class CategoryRecursionParentError(ApplicationError):
    """Возникает, когда категория ссылается на саму себя в parent_id"""

    pass


class ChildCategoryExistsError(ApplicationError):
    """Возникает, когда происходит попытка удаления категории, у которой есть потомки"""

    pass
