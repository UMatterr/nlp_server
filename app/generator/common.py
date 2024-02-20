import torch
from utils import generate
from transformers import GPT2LMHeadModel, AutoTokenizer

class CommonGenerator():
    """gpt2 기반 transformer 모델로 text를 생성하기 위한 클래스
    """
    model = None
    tokenizer = None
    train_prefix = ''

    def __init__(self, model_path, token_path, train_prefix):
        self.model = GPT2LMHeadModel.from_pretrained(model_path, resume_download=True)
        self.tokenizer = AutoTokenizer.from_pretrained(token_path)
        device = "cuda:0" if torch.cuda.is_available() else "cpu" 
        self.model = self.model.to(device)
        self.train_prefix = train_prefix

    def generate(self):
	    return generate(self.train_prefix, self.tokenizer, self.model, 1)[0]

    def generateN(self, num):
	    return generate(self.train_prefix, self.tokenizer, self.model, num)

