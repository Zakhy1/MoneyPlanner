class ApplicationError(Exception):
    """Базовое исключение для приложения."""

    pass


class ObjectDoesNotExists(ApplicationError):
    """Базовое исключение для ситуаций, когда объект не найден."""

    pass


class CategoryDoesNotExists(ObjectDoesNotExists):
    """Возникает, когда искомая категория не найдена."""

    pass


class ParentCategoryDoesNotExists(CategoryDoesNotExists):
    """Возникает, когда искомая категория не найдена."""

    pass


class CategoryDirectionMismatch(ApplicationError):
    """Возникает, когда direction родительской и дочерней категории различаются."""

    pass
