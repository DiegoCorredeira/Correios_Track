import unittest
from unittest.mock import patch
from main import CorreiosTracker


class TestCorreiosTracker(unittest.TestCase):
    @patch("requests.get")
    def test_rastrear_encomenda_valid(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "eventos": [
                {
                    "data": "11/08/2023",
                    "hora": "23:27",
                    "local": "Curitiba / PR",
                    "status": "Objeto encaminhado",
                    "subStatus": ["Origem: Unidade de Tratamento - Curitiba / PR"]
                }
            ]
        }

        tracker = CorreiosTracker(None)
        result = tracker.rastrear_encomenda("LB577473955HK")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["local"], "Curitiba / PR")
        self.assertEqual(result[0]["status"], "Objeto encaminhado")
        self.assertEqual(result[0]["subStatus"], ["Origem: Unidade de Tratamento - Curitiba / PR"])

    def test_formatar_resultado(self):
        evento = {
            "data": "11/08/2023",
            "hora": "23:27",
            "local": "Curitiba / PR",
            "status": "Objeto encaminhado",
            "subStatus": ["Origem: Unidade de Tratamento - Curitiba / PR"]
        }
        tracker = CorreiosTracker(None)
        formatted_result = tracker.formatar_resultado([evento])

        expected_result = "Data: 11/08/2023\nHora: 23:27\nLocal: Curitiba / PR\nStatus: Objeto encaminhado\nSubStatus:\n  - Origem: Unidade de Tratamento - Curitiba / PR\n\n"
        self.assertEqual(formatted_result, expected_result)


if __name__ == "__main__":
    unittest.main()
