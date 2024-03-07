###Using the current generation pipeline is not sufficient. Therefore, I have concluded that I should try the following approaches:

1) Generating text using ChatGPT and LangChain,

2) Fine-tuning an existing model, and

3) Exploring other approaches



---


from transformers import AutoModel, AutoTokenizer, BertTokenizer
from transformers import pipeline

pipe = pipeline("text-generation", model="skt/kogpt2-base-v2", max_length=30)
pipe("2024년 갑진년 청룡의")

[{'generated_text': '2024년 갑진년 청룡의 재등장을 목표로 하고 있으며 2025년 을질상 수상 후보군인 윤영대 선수와 김한수 선'}]
