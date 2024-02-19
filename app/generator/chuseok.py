import torch
from utils import generate
from transformers import GPT2LMHeadModel, AutoTokenizer

class ChuseokGenerator():
    model = None
    tokenizer = None

    def __init__(self):
        self.model = GPT2LMHeadModel.from_pretrained("UMatterr/chuseok", resume_download=True)
        self.tokenizer = AutoTokenizer.from_pretrained("skt/kogpt2-base-v2")
        device = "cuda:0" if torch.cuda.is_available() else "cpu" 
        self.model = self.model.to(device)

    def generate(self):
	    return generate('추석8565', self.tokenizer, self.model, 1)[0]
