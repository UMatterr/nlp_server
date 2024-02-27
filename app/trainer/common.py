import torch
from tqdm import tqdm
from utils import generate
from transformers import GPT2LMHeadModel, AutoTokenizer, AdamW, get_linear_schedule_with_warmup
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from io import StringIO

class GPTDataset(Dataset):
    def __init__(self, tokenizer, file_paths, buffer_list):
        concats = []
        if file_paths != None:
            for file_path in file_paths:
                data = pd.read_csv(file_path, sep='|')
                concats += [
                    label + "|" + text for label, text in zip(data["target"], data["text"])
                ]
        if buffer_list != None:
            for buffer in buffer_list:
                data = pd.read_csv(StringIO(buffer), sep='|')
                concats += [
                    label + "|" + text for label, text in zip(data["target"], data["text"])
                ]

        self.item = tokenizer(
            concats,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=32,
        )["input_ids"]

        self.length = len(concats)

    def __getitem__(self, i):
        return self.item[i]

    def __len__(self):
        return self.length


def GPTDataLoader(tokenizer, file_paths, buffer_list, batch_size):
    data = GPTDataset(tokenizer, file_paths, buffer_list)
    return DataLoader(data, batch_size=batch_size)


class CommonTrainer():
    """gpt2 기반 transformer 모델을 훈련하기 위한 클래스
    """
    model = None
    best_model = None
    tokenizer = None
    device = None
    train_prefix = ''

    def __init__(self, model_path, token_path, train_prefix):
        self.model = GPT2LMHeadModel.from_pretrained(model_path, resume_download=True)
        self.tokenizer = AutoTokenizer.from_pretrained(token_path)
        self.tokenizer.add_special_tokens({"pad_token": "<pad>"})
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu" 
        self.model = self.model.to(self.device)
        self.train_prefix = train_prefix

    def train(self, data):

        trained = False

        train_dataloader = GPTDataLoader(
            self.tokenizer, None, [data], 32 # TODO: 설정 가능하도록
        ) 
        self.model.train()
        
        optimizer = AdamW(self.model.parameters(), lr=2e-5) # TODO: 설정 가능하도록
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps = 200, num_training_steps = -1 # TODO: 설정 가능하도록
        )

        # DEBUG: 
        epochs = 1 #4 # TODO: 설정 가능하도록
        min_loss = int(100)

        for epoch in range(epochs):
            print(f"Training epoch {epoch}")
            for input_text in tqdm(train_dataloader):
                input_tensor = input_text.to(self.device)
                outputs = self.model(input_tensor, labels=input_tensor)
                loss = outputs[0]

                optimizer.zero_grad()
                self.model.zero_grad()
                loss.backward()
                optimizer.step()
                scheduler.step()

            print(f"epoch {epoch} loss {outputs[0].item():0.2f}")

            # Save best model
            if outputs[0].item() < min_loss:
                print(f"save min loss model: {outputs[0].item()}")
                self.best_model = self.model
                self.best_model.save_pretrained("./best_model")
                trained = True

        return trained

    def push(self, path, token_path):
        token = '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'
        self.best_model = GPT2LMHeadModel.from_pretrained("./best_model")
        self.best_model = self.best_model.to(self.device)
        self.best_model.push_to_hub(path, use_temp_dir=True, use_auth_token=token)
        self.tokenizer.push_to_hub(token_path, use_temp_dir=True, use_auth_token=token)
        return True

