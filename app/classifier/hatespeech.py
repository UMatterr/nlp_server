import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW, TrainingArguments, Trainer


class HatespeechClassifier():
    model = None
    tokenizer = None
    device = None

    def __init__(self):
        self.model = AutoModelForSequenceClassification.from_pretrained("UMatterr/bad_words", resume_download=True)
        self.tokenizer = AutoTokenizer.from_pretrained("UMatterr/bad_words")
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu" 
        self.model = self.model.to(self.device)

    def is_hate(self, sent):
        # 평가모드로 변경
        self.model.eval()

        # 입력된 문장 토크나이징
        tokenized_sent = self.tokenizer(sent, return_tensors='pt', max_length=500, padding=True, truncation=True, add_special_tokens=True)

        tokenized_sent.to(self.device)

        # 예측
        with torch.no_grad():
            outputs = self.model(input_ids=tokenized_sent['input_ids'], attention_mask=tokenized_sent['attention_mask'], token_type_ids=tokenized_sent['token_type_ids'])

        logits = outputs[0]
        logits = logits.detach().cpu()
        result = logits.argmax(-1)
        return result[0].numpy()
