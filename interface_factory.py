from rdkit import Chem
from typing import Dict, List, Callable, Mapping, Any, TypedDict, Tuple
import json, enum

# example standardized errors... that are used both by interface and wrapped app

class UserError(Exception):
    """
    The user screwed up.
    """
    pass


class AppError(Exception):
    """
    The code screwed up.
    """
    pass


class IneffectiveSettingsError(Exception):
    """
    The code did not find anything but it worked
    """
    pass


# ----------------------------------------
class JSAction(enum.Enum):
    show_toast = 0
    show_LHS_hits = 1
    add_RHS_hits = 2
    show_modal = 3
    other_JS = 4

class OutputType(TypedDict):
    """
    A standarized output
    """
    status: str  # 'error' or 'success'
    results: Any  # jsonable
    action: str  # a JS action name (from JSAction enum)


class FauxInterfaceFactory:
    """
    An example interface factory. Not real.

    ... code-block::python
        myapp = FauxInterfaceFactory(main)
        front_end_requirements = myapp.front_end_fields
        output: OutputType = myapp(inputs)

    """

    def __init__(self, fun: Callable):
        self.fun = fun

    def __call__(self, inputs: Mapping) -> OutputType:
        try:
            results: Any
            action: JSAction
            results, action = self.error_sanitized_call(inputs)
            return dict(status='success',
                        results=results,
                        action=action.name)
        except (UserError, IneffectiveSettingsError, AppError) as error:
            error_type = error.__class__.__name__
            return dict(status='error',
                        results={'error_type': error_type,
                                 'msg': str(error)},
                        action=JSAction.show_toast.name,
                        )

    def error_sanitized_call(self, inputs) -> Tuple[Any, JSAction]:
        try:
            outputs: Any = self.fun(**inputs)
            if self.is_valid_json(outputs):
                return outputs
            raise AppError('Invalid output')
        except Exception as error:
            raise AppError(f'{error.__class__.__name__}: {error}')

    def is_valid_json(self, obj):
        try:
            json.dumps(obj)
            return True
        except (TypeError, OverflowError):
            return False

    # --------------------------------------------------------
    # some code to dynamically define frontend say...
    # this is terrible, but is a placeholder
    python2html_mapping = {str: 'input type="text" name="{name}"',
                           int: 'input type="number" step="1" name="{name}"',
                           float: 'input type="number" name="{name}"',
                           }

    @property
    def front_end_fields(self):
        return {key: self.python2html_mapping[value].format(name=key) for key, value in self.fun.__annotations__.items()
                if key != 'return'}

    # ----------------------------------------

    @staticmethod
    def get_sdf_block(sdf):