import unittest

from payload_validator import validate_payload


class PayloadValidatorTest(unittest.TestCase):
    """Basic coverage to ensure the validator catches bad shapes."""

    def _sample_payload(self) -> dict:
        return {
            "id": "deadbeef",
            "timestamp": "2022-08-26T18:47:33Z",
            "network": "testnet",
            "op_type": "mint",
            "target": "0xabc",
            "amount": 10,
        }

    def test_missing_required_keys(self) -> None:
        payload = self._sample_payload()
        payload.pop("network")
        with self.assertRaises(ValueError):
            validate_payload(payload)

    def test_negative_amount_rejected(self) -> None:
        payload = self._sample_payload()
        payload["amount"] = -5
        with self.assertRaises(ValueError):
            validate_payload(payload)

    def test_successful_payload(self) -> None:
        payload = self._sample_payload()
        validate_payload(payload)


if __name__ == "__main__":
    unittest.main()
