

import torch
import numpy as np
from preprocessing import preprocess_urls


class CharExplainer:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.device = next(model.parameters()).device

    def _predict_proba(self, text: str) -> np.ndarray:
        """Get class probabilities for a single text input."""
        inputs = self.tokenizer(
            text, return_tensors="pt",
            padding="max_length", truncation=True, max_length=128
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        return probs.cpu().numpy()[0]

    def explain(self, url: str):
        """
        Compute character-level importance scores using leave-one-out.

        Returns a list of {"char": str, "importance": float} dicts.
        """
        cleaned_url = preprocess_urls([url])[0]

        baseline_probs = self._predict_proba(cleaned_url)
        pred_class = int(np.argmax(baseline_probs))
        baseline_conf = float(baseline_probs[pred_class])

        char_importances = []
        for i, char in enumerate(cleaned_url):
            masked = cleaned_url[:i] + '_' + cleaned_url[i + 1:]
            masked_probs = self._predict_proba(masked)
            masked_conf = float(masked_probs[pred_class])

            importance = baseline_conf - masked_conf

            char_importances.append({
                "char": char,
                "importance": round(importance, 6)
            })

        return char_importances
