// Llama al servidor Flask y pinta la respuesta en la página.
async function RunSentimentAnalysis() {
    const textToAnalyze = document.getElementById("textToAnalyze").value;
    const output = document.getElementById("system_response");

    try {
        const response = await fetch(
            "/emotionDetector?textToAnalyze=" + encodeURIComponent(textToAnalyze)
        );
        output.textContent = await response.text();
    } catch (error) {
        output.textContent = "No se pudo contactar con el servidor.";
    }
}
