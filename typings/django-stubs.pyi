# Django Model Stubs for Pylance
from typing import Any, Optional, Union, List, Tuple

class Model:
    def save(self, *args: Any, **kwargs: Any) -> None: ...
    def delete(self, *args: Any, **kwargs: Any) -> Tuple[int, dict]: ...
    def refresh_from_db(self, using: Optional[str] = None, instance: Optional['Model'] = None) -> None: ...

class CharField:
    def get_FOO_display(self) -> str: ...  # Django generates this for choices fields

class IntegerField:
    pass

class DecimalField:
    pass

class DateField:
    pass

class DateTimeField:
    pass

class BooleanField:
    pass

class EmailField:
    pass

class TextField:
    pass

class ForeignKey:
    pass

class OneToOneField:
    pass

class ManyToManyField:
    pass

class AutoField:
    pass

class PositiveIntegerField:
    pass

# Common Django model methods
def __str__(self) -> str: ...
def __repr__(self) -> str: ...
