import pytest

from aissist.model import Model
from aissist.exceptions import InvalidParameterError

def test_instantiation__invalid_model():
    """Test that an InvalidParameterError is raised when an invalid model is passed
    to Model"""

    with pytest.raises(InvalidParameterError):
        Model("not-a-real-model")