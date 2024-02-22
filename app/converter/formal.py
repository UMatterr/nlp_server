import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

class ToFormalConverter():
    """존댓말 변환 모델
    """
    model = None
    tokenizer = None
    device = None

    def __init__(self):
        self.model = T5ForConditionalGeneration.from_pretrained("UMatterr/toformal", resume_download=True)
        self.tokenizer = T5Tokenizer.from_pretrained("UMatterr/toformal")
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu" 
        self.model = self.model.to(self.device)

    def convert(self, input_text):
        input_encoding = self.tokenizer("존댓말로 바꿔주세요: " + input_text, return_tensors="pt")

        input_ids = input_encoding.input_ids.to(self.device)
        attention_mask = input_encoding.attention_mask.to(self.device)

        output_encoding = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=256,
            num_beams=5,
            early_stopping=True,
        )
        output_text = self.tokenizer.decode(output_encoding[0], skip_special_tokens=True)
        return output_text