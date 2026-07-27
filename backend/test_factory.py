from app.normalizer.factory import normalizer_factory

from app.normalizer.aws import AWSNormalizer
from app.normalizer.azure import AzureNormalizer
from app.normalizer.gcp import GCPNormalizer
from app.normalizer.base import BaseNormalizer


def test_factory():

    assert isinstance(
        normalizer_factory.get_normalizer("AWS"),
        AWSNormalizer
    )

    assert isinstance(
        normalizer_factory.get_normalizer("AZURE"),
        AzureNormalizer
    )

    assert isinstance(
        normalizer_factory.get_normalizer("GCP"),
        GCPNormalizer
    )

    assert isinstance(
        normalizer_factory.get_normalizer("UNKNOWN"),
        BaseNormalizer
    )


if __name__ == "__main__":

    test_factory()

    print("✅ Factory Test Passed")
