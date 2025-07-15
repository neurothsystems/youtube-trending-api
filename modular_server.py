# modular_server.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from trending_algorithm import (
    V6TrendingAnalyzer,
    # Füge weitere Analyzer-Klassen hinzu, falls du sie verwendest:
    # BasicAnalyzer, RegionalAnalyzer, AntiSpamAnalyzer, ExperimentalAnalyzer
)
import logging

app = FastAPI(
    title="TopMetric Modular API",
    version="1.0.0"
)

# Algorithmus-Factory
ANALYZERS = {
    "v6": V6TrendingAnalyzer,
    # "basic": BasicAnalyzer,
    # "regional": RegionalAnalyzer,
    # "anti_spam": AntiSpamAnalyzer,
    # "experimental": ExperimentalAnalyzer,
}

# Logger konfigurieren
logger = logging.getLogger("uvicorn.error")

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    query = data.get("query")
    region = data.get("region", "DE")
    algorithm = data.get("algorithm", "v6")
    kwargs = {k: v for k, v in data.items() if k not in ["query", "region", "algorithm"]}

    # Algorithmus-Check
    if algorithm not in ANALYZERS:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": f"Algorithm '{algorithm}' not available.",
                "available_algorithms": list(ANALYZERS.keys()),
            }
        )

    AnalyzerClass = ANALYZERS[algorithm]

    try:
        # Doppeltes target_region vermeiden!
        if "target_region" in kwargs:
            del kwargs["target_region"]

        analyzer = AnalyzerClass(query, region, **kwargs)
        result = analyzer.analyze()
        return JSONResponse(
            status_code=200,
            content=result
        )
    except Exception as e:
        logger.error(f"Error in /analyze: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Analysis failed: {e}",
                "details": str(e),
                "available_algorithms": list(ANALYZERS.keys())
            }
        )

@app.get("/health")
async def health():
    return {"status": "ok"}

# Falls du weitere Endpunkte hast (z. B. /export, /admin, /log), hier ergänzen...

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
