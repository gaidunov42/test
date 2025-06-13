from sqlalchemy.inspection import inspect


class BaseModelMixin:
    def to_dict(self) -> dict:
        """
        Преобразует SQLAlchemy-модель в словарь.
        """
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
