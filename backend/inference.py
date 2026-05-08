import torch
from transformers import CanineForSequenceClassification, CanineTokenizer
from preprocessing import preprocess_urls

class PhishDetector:
    def __init__(self, model_path="./saved_model"):
        print(f"Loading model and tokenizer from {model_path}...")
        self.tokenizer = CanineTokenizer.from_pretrained(model_path)
        self.model = CanineForSequenceClassification.from_pretrained(model_path)
        self.model.eval()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        self.labels = {0: "Safe", 1: "Homograph", 2: "Phishing"}
        
    def predict(self, url: str):
        cleaned_url = preprocess_urls([url])[0]
        inputs = self.tokenizer(cleaned_url, return_tensors="pt", padding="max_length", truncation=True, max_length=128).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        confidence, pred_idx = torch.max(probs, dim=-1)
        
        return {
            "prediction": self.labels.get(pred_idx.item(), "Unknown"),
            "confidence": float(confidence.item()),
            "cleaned_url": cleaned_url
        }
