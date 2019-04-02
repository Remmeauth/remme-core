from decimal import Decimal

from remme.shared.utils import client_to_real_amount, real_to_client_amount


DIVISIBILITY_FACTOR = 4


def test_client_to_real_amount_accuracy():
    result = client_to_real_amount(1, DIVISIBILITY_FACTOR)
    assert result == 10000


def test_client_to_real_amount_rounding():
    result2 = client_to_real_amount(0, DIVISIBILITY_FACTOR)
    assert result2 == 0

    result2 = client_to_real_amount(0.5, DIVISIBILITY_FACTOR)
    assert result2 == 5000

    result3 = client_to_real_amount(0.50005, DIVISIBILITY_FACTOR)
    assert result3 == 5001

    result4 = client_to_real_amount(0.50006, DIVISIBILITY_FACTOR)
    assert result4 == 5001


def test_real_to_client_amount_accuracy():
    result = real_to_client_amount(1, DIVISIBILITY_FACTOR)
    assert result == Decimal('0.0001')


def test_real_to_client_amount_rounding():
    result = real_to_client_amount(0.5, DIVISIBILITY_FACTOR)
    assert result == Decimal('0.0001')

    result2 = real_to_client_amount(1.4315, DIVISIBILITY_FACTOR)
    assert result2 == Decimal('0.0001')

    result3 = real_to_client_amount(1.5714, DIVISIBILITY_FACTOR)
    assert result3 == Decimal('0.0002')

    result4 = real_to_client_amount(2514.1452, DIVISIBILITY_FACTOR)
    assert result4 == Decimal('0.2514')

    result5 = real_to_client_amount(142453.1452, DIVISIBILITY_FACTOR)
    assert result5 == Decimal('14.2453')

    result6 = real_to_client_amount(0, DIVISIBILITY_FACTOR)
    assert result6 == Decimal('0.0000')

