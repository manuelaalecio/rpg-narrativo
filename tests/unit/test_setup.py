import application
import config
import domain
import infrastructure
import presentation
import services
import ui


def test_all_packages_importable():
    assert domain is not None
    assert application is not None
    assert infrastructure is not None
    assert presentation is not None
    assert ui is not None
    assert services is not None
    assert config is not None
