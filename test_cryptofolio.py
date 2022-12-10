import pytest
from cryptofolio import total_value
from cryptofolio import new_user
from cryptofolio import title

@pytest.fixture
def sample_port():
    return  {
            "btc": {
                    "amount": 2,
                    "value": 30000,
            },
            "eth": {
                    "amount": 1.8,
                    "value": 2500,
            },
    }


def test_total_value(sample_port):
  assert total_value(sample_port) == 32500

def test_new_user():
  assert new_user() == None

def test_title():
  assert type(title()) == type("")
