import swapanything
from packaging import version


def test_version() -> None:
    """Test that package has version, is semver and >= '0.0.1.dev0'"""
    # Test that package has readable version
    assert isinstance(swapanything.__version__, str)
    # Test that package has compliant semver
    assert version.Version(swapanything.__version__)
    # Test that package has semver greater or equal than '0.0.1.dev0'
    assert version.Version(swapanything.__version__) >= version.Version("0.0.1.dev0")
