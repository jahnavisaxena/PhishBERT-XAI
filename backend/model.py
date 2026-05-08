from transformers import CanineTokenizer, CanineForSequenceClassification
import torch

def get_model_and_tokenizer(model_name="google/canine-c", num_labels=3):
    """
    Loads CANINE-c model and tokenizer for sequence classification.
    Classes: 0 -> Safe, 1 -> Homograph, 2 -> Phishing
    """
    print(f"Loading tokenizer {model_name}...")
    tokenizer = CanineTokenizer.from_pretrained(model_name)
    
    print(f"Loading model {model_name}...")
    model = CanineForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
    
    return model, tokenizer

if __name__ == "__main__":
    model, tokenizer = get_model_and_tokenizer()
    print("Model and Tokenizer loaded successfully.")
