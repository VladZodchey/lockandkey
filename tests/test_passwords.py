from ..src.utils.passwords import generate_password, Security
from ..src.utils.characters import PASSWORD_CHARS

import pytest


class TestPasswordEvaluations:
    def test_gen_with_ok_length(self):
        assert len(generate_password(length=16)) == 16
    def test_gen_with_zero_length(self):
        password = generate_password(length=0)
        assert len(password) == 0
    def test_gen_with_neg_length(self):
        with pytest.raises(ValueError):
            _ = generate_password(length = -1)

    def test_gen_with_ok_charset(self):
        assert all(i in PASSWORD_CHARS for i in generate_password(PASSWORD_CHARS))
    def test_gen_with_empty_charset(self):
        with pytest.raises(ValueError):
            _ = generate_password(set())
    def test_gen_with_not_set(self):
        ...
