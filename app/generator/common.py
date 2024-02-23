import torch
from utils import generate
from transformers import GPT2LMHeadModel, AutoTokenizer

def args2dict(args):
    if args[0] != None:
        return {"eos_token":args[0]}
    else:
        return {}

class CommonGenerator():
    """gpt2 기반 transformer 모델로 text를 생성하기 위한 클래스
    """
    model = None
    tokenizer = None
    train_prefix = ''

    def __init__(self, model_path, token_path, train_prefix, args):

        dict_args = args2dict(args)
        self.model = GPT2LMHeadModel.from_pretrained(model_path, resume_download=True)
        self.tokenizer = AutoTokenizer.from_pretrained(token_path, **dict_args)
        device = "cuda:0" if torch.cuda.is_available() else "cpu" 
        self.model = self.model.to(device)
        self.train_prefix = train_prefix

    def generate(self, args):
	    return generate(self.train_prefix, self.tokenizer, self.model, 1, args)[0]

    def generateN(self, num, args):
	    return generate(self.train_prefix, self.tokenizer, self.model, num, args)

