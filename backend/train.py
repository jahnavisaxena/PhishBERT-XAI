import torch
from transformers import Trainer, TrainingArguments
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import argparse

from data_loader import load_and_split_data
from preprocessing import preprocess_urls
from model import get_model_and_tokenizer

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='macro', zero_division=0)
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def train(sample_size=None, output_dir="./saved_model", epochs=3, batch_size=16):
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = load_and_split_data(sample_size=sample_size)
    
    X_train = preprocess_urls(X_train)
    X_val = preprocess_urls(X_val)
    X_test = preprocess_urls(X_test)
    
    model, tokenizer = get_model_and_tokenizer(num_labels=3)
    
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        model.resize_token_embeddings(len(tokenizer))
    
    def tokenize_data(texts, labels):
        encodings = tokenizer(texts, padding="max_length", truncation=True, max_length=128)
        dataset = Dataset.from_dict({
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'label': labels
        })
        return dataset

    print("Tokenizing datasets...")
    train_dataset = tokenize_data(X_train, y_train)
    val_dataset = tokenize_data(X_val, y_val)
    test_dataset = tokenize_data(X_test, y_test)
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_steps=min(500, len(train_dataset) // 2), # avoid large warmup on tiny sets
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    print("Starting training...")
    trainer.train()
    
    print("Evaluating on test set...")
    results = trainer.evaluate(test_dataset)
    print("Test Results:", results)
    
    print(f"Saving model to {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tiny", action="store_true", help="Run with a tiny sample for local verification")
    args = parser.parse_args()
    
    if args.tiny:
        print("Running locally with a tiny sample (for verification only).")
        train(sample_size=100, epochs=1, batch_size=4)
    else:
        print("Running full training...")
        train()
