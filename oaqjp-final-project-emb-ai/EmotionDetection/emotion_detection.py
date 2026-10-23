"""Detección de emociones en texto mediante la librería Watson NLP (IBM).

El módulo expone una única función pública, ``emotion_detector``, que:

1. envía el texto a la API REST de Watson,
2. interpreta la respuesta JSON,
3. devuelve las cinco emociones con su puntuación y la emoción dominante.

La URL del servicio puede cambiarse con la variable de entorno
``WATSON_EMOTION_URL`` (útil para pruebas o si IBM cambia el endpoint).
"""

import os

import requests

DEFAULT_URL = (
    "https://sn-watson-emotion.labs.skills.network"
    "/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict"
)
MODEL_ID = "emotion_aggregated-workflow_lang_en_stock"
EMOTIONS = ("anger", "disgust", "fear", "joy", "sadness")
TIMEOUT_SECONDS = 10


def _empty_result():
    """Resultado "vacío": todas las claves existen pero con valor ``None``."""
    result = {emotion: None for emotion in EMOTIONS}
    result["dominant_emotion"] = None
    return result


def parse_response(payload):
    """Convierte el JSON de Watson en un diccionario plano.

    Args:
        payload: diccionario ya decodificado desde el JSON de respuesta.

    Returns:
        dict con las claves ``anger``, ``disgust``, ``fear``, ``joy``,
        ``sadness`` y ``dominant_emotion``.
    """
    scores = payload["emotionPredictions"][0]["emotion"]
    result = {emotion: scores[emotion] for emotion in EMOTIONS}
    result["dominant_emotion"] = max(EMOTIONS, key=lambda name: result[name])
    return result


def emotion_detector(text_to_analyze):
    """Analiza ``text_to_analyze`` y devuelve sus emociones.

    Si el texto está vacío o el servicio responde con error 400, todas las
    claves del diccionario devuelto valen ``None``. Así la capa web puede
    decidir qué mensaje enseñar sin tener que capturar excepciones.
    """
    if not text_to_analyze or not text_to_analyze.strip():
        return _empty_result()

    url = os.environ.get("WATSON_EMOTION_URL", DEFAULT_URL)
    headers = {"grpc-metadata-mlmodel-id": MODEL_ID}
    body = {"raw_document": {"text": text_to_analyze}}

    try:
        response = requests.post(
            url, json=body, headers=headers, timeout=TIMEOUT_SECONDS
        )
    except requests.RequestException:
        return _empty_result()

    if response.status_code != 200:
        return _empty_result()

    try:
        return parse_response(response.json())
    except (KeyError, IndexError, ValueError):
        return _empty_result()
