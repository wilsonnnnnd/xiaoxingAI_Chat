import requests

prompt = "你是谁？"
system_prompt = open("E:/xiaoxing/prompt.txt", encoding="utf-8").read()
full_prompt = system_prompt + "\n用户：" + prompt + "\n小星："

response = requests.post("http://127.0.0.1:8000/completion", json={
    "prompt": full_prompt,
    "n_predict": 128,
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
})

print(response.status_code)
print(response.json())
