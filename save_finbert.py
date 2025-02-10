from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "ProsusAI/finbert"

# Download model from Hugging Face
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Save locally
save_directory = "./finbert_model"
tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)

print("FinBERT model saved successfully!")
