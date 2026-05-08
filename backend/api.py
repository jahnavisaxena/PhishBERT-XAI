from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

from inference import PhishDetector
from explainability import CharExplainer
from url_analyzer import analyze_url

app = FastAPI(title="PhishBERT-XAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = None
explainer = None

@app.on_event("startup")
def load_models():
    global detector, explainer
    model_path = "./saved_model/saved_model"
    if not os.path.exists(model_path):
        print(f"WARNING: Model path {model_path} does not exist. Please run training first.")
        print("Falling back to un-finetuned google/canine-c for testing purposes.")
        model_path = "google/canine-c"
        
    try:
        detector = PhishDetector(model_path)
        explainer = CharExplainer(detector.model, detector.tokenizer)
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")

class URLRequest(BaseModel):
    url: str

@app.post("/predict")
def predict_url(req: URLRequest):
    if not req.url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    if detector is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    try:
        result = detector.predict(req.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain")
def explain_url(req: URLRequest):
    if not req.url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    if explainer is None or detector is None:
        raise HTTPException(status_code=500, detail="Model/Explainer not loaded")
        
    try:
        pred_result = detector.predict(req.url)
        shap_values = explainer.explain(req.url)
        
        return {
            "prediction": pred_result["prediction"],
            "confidence": pred_result["confidence"],
            "shap_values": shap_values
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze(req: URLRequest):
    if not req.url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    try:
        return analyze_url(req.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
