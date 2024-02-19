import torch
from utils import generate
from transformers import GPT2LMHeadModel, AutoTokenizer

class CommonTrainer():
    model = None
    tokenizer = None
    train_prefix = ''

    def __init__(self, model_path, token_path, train_prefix):
        #self.model = GPT2LMHeadModel.from_pretrained("UMatterr/chuseok", resume_download=True)
        #self.tokenizer = AutoTokenizer.from_pretrained("skt/kogpt2-base-v2")
        self.model = GPT2LMHeadModel.from_pretrained(model_path, resume_download=True)
        self.tokenizer = AutoTokenizer.from_pretrained(token_path)
        device = "cuda:0" if torch.cuda.is_available() else "cpu" 
        self.model = self.model.to(device)
        self.train_prefix = train_prefix

    def train(self, data):
        return true

    def push(self, path, token_path):
        token = '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'
        self.model.push_to_hub(path, use_temp_dir=True, use_auth_token=token)
        self.tokernizer.push_to_hub(token_path, use_temp_dir=True, use_auth_token=token)

