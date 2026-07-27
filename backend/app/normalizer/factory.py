from app.normalizer.base import BaseNormalizer
from app.normalizer.aws import aws_normalizer
from app.normalizer.azure import azure_normalizer
from app.normalizer.gcp import gcp_normalizer


class NormalizerFactory:

    def __init__(self):
        self.base = BaseNormalizer()

    def get_normalizer(self, provider):

        provider = str(provider).upper()

        normalizers = {
            "AWS": aws_normalizer,
            "AZURE": azure_normalizer,
            "GCP": gcp_normalizer,
        }

        return normalizers.get(provider, self.base)


normalizer_factory = NormalizerFactory()