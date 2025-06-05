from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load the pre-trained T5 model and tokenizer
model_name = "t5-small"  # You can use other variants like 't5-base' or 't5-large' for better performance
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name)

def generate_notification(problem_log):
    """Generate a human-readable alert using T5 model."""
    # Format the input as a text-to-text task for T5
    input_text = f"Generate a human-readable alert for the following issue: {problem_log}"
    
    # Tokenize the input text and pass it through the model
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=100, num_beams=4, early_stopping=True)
    
    # Decode the model output and return the alert message
    alert_message = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return alert_message

