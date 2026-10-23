"""Pruebas de la capa web (Flask) usando el cliente de pruebas."""

import unittest
from unittest.mock import patch

from server import app


class TestServer(unittest.TestCase):
    """Verifica rutas y mensajes de la aplicación."""

    def setUp(self):
        self.client = app.test_client()

    def test_index_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Emotion Detector", response.data)

    def test_valid_text_formats_message(self):
        fake = {"anger": 0.1, "disgust": 0.1, "fear": 0.1, "joy": 0.9,
                "sadness": 0.1, "dominant_emotion": "joy"}
        with patch("server.emotion_detector", return_value=fake):
            response = self.client.get("/emotionDetector?textToAnalyze=I+love+it")
        text = response.get_data(as_text=True)
        self.assertIn("The dominant emotion is joy.", text)

    def test_blank_text_returns_error_message(self):
        response = self.client.get("/emotionDetector?textToAnalyze=")
        self.assertEqual(
            response.get_data(as_text=True), "Invalid text! Please try again!"
        )


if __name__ == "__main__":
    unittest.main()
