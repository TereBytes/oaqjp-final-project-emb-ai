"""Pruebas unitarias del detector de emociones.

Se usa ``unittest.mock`` para simular la API de Watson, de modo que los tests
funcionan sin red y son deterministas (esto es lo que se espera en CI).
"""

import unittest
from unittest.mock import MagicMock, patch

from EmotionDetection.emotion_detection import emotion_detector, parse_response


def fake_watson_response(**scores):
    """Construye una respuesta falsa con el formato real de Watson."""
    base = {"anger": 0.01, "disgust": 0.01, "fear": 0.01, "joy": 0.01, "sadness": 0.01}
    base.update(scores)
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"emotionPredictions": [{"emotion": base}]}
    return response


class TestEmotionDetector(unittest.TestCase):
    """Comprueba la emoción dominante para cada frase de ejemplo."""

    CASES = (
        ("I am glad this happened", "joy"),
        ("I am really mad about this", "anger"),
        ("I feel disgusted just hearing about this", "disgust"),
        ("I am so sad about this", "sadness"),
        ("I am really afraid that this will happen", "fear"),
    )

    def test_dominant_emotion(self):
        for text, expected in self.CASES:
            with self.subTest(text=text):
                with patch(
                    "EmotionDetection.emotion_detection.requests.post",
                    return_value=fake_watson_response(**{expected: 0.9}),
                ):
                    result = emotion_detector(text)
                self.assertEqual(result["dominant_emotion"], expected)

    def test_result_has_all_keys(self):
        with patch(
            "EmotionDetection.emotion_detection.requests.post",
            return_value=fake_watson_response(joy=0.8),
        ):
            result = emotion_detector("I love my life")
        self.assertEqual(
            set(result),
            {"anger", "disgust", "fear", "joy", "sadness", "dominant_emotion"},
        )

    def test_empty_text_returns_none_values(self):
        result = emotion_detector("")
        self.assertTrue(all(value is None for value in result.values()))

    def test_status_400_returns_none_values(self):
        bad = MagicMock()
        bad.status_code = 400
        with patch(
            "EmotionDetection.emotion_detection.requests.post", return_value=bad
        ):
            result = emotion_detector("   ")
        self.assertIsNone(result["dominant_emotion"])

    def test_parse_response_picks_highest_score(self):
        payload = {
            "emotionPredictions": [
                {"emotion": {"anger": 0.1, "disgust": 0.2, "fear": 0.3,
                             "joy": 0.05, "sadness": 0.35}}
            ]
        }
        self.assertEqual(parse_response(payload)["dominant_emotion"], "sadness")


if __name__ == "__main__":
    unittest.main()
