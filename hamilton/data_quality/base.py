import abc
from typing import Type, Any, List, Dict

import dataclasses


class DataValidationError:
    pass


@dataclasses.dataclass
class ValidationResult:
    passes: bool  # Whether or not this passed the validation
    message: str  # Error message or success message
    diagnostics: Dict[str, Any] = dataclasses.field(default_factory=dict)  # Any extra diagnostics information needed, free-form


class DataValidator(abc.ABC):
    """Base class for a data quality operator. This will be used by the `data_quality` operator"""
    # Importance levels
    WARN = 'warn'
    FAIL = 'fail'

    VALID_IMPORTANCES = {WARN, FAIL}  # TODO -- think through the API

    @staticmethod
    def validate_importance_level(importance: str):
        if importance not in DataValidator.VALID_IMPORTANCES:
            raise ValueError(f'Importance level must be one of: {DataValidator.VALID_IMPORTANCES}')

    @abc.abstractmethod
    def applies_to(self, datatype: Type[Type]) -> bool:
        """Whether or not this data validator can apply to the specified dataset

        :param datatype:
        :return: True if it can be run on the specified type, false otherwise
        """
        pass

    @abc.abstractmethod
    def description(self) -> str:
        """Gives a description of this validator. E.G.
        `Checks whether the entire dataset lies between 0 and 1.`
        Note it should be able to access internal state (E.G. constructor arguments).
        :return: The description of the validator as a string
        """
        pass

    @abc.abstractmethod
    def validate(self, dataset: Any) -> ValidationResult:
        """Actually performs the validation. Note when you

        :param dataset:
        :return:
        """
        pass

    def required_config(self) -> List[str]:
        """Gets the required configuration items. These are likely passed in in construction
        (E.G. in the constructor parameters).

        :return: A list of required configurations
        """
        return []

    def dependencies(self) -> List[str]:
        """Nodes upon which this depends. For example,
        this might depend on a node that provides the output from the
        last run of this DAG to execute an auto-correlation.

        :return: The list of node-name dependencies.
        """
        return []
