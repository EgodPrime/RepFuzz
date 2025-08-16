import openai

from repfuzz.config import CHAT_LLM

client = openai.OpenAI(base_url=CHAT_LLM.base_url, api_key=CHAT_LLM.api_key)
async_client = openai.AsyncOpenAI(base_url=CHAT_LLM.base_url, api_key=CHAT_LLM.api_key)


def complete(prompt: str) -> str:
    res = client.completions.create(model=CHAT_LLM.model_name, prompt=prompt, stop="<END>")
    t = res.choices[0].text
    if t is None:
        return ""
    return t


async def async_complete(prompt: str) -> str:
    res = await async_client.completions.create(
        model=CHAT_LLM.model_name,
        prompt=prompt,
        stop="<END>",
        max_tokens=1024,
    )
    return res.choices[0].text


def chat(prompt: str) -> str:
    res = client.chat.completions.create(
        model=CHAT_LLM.model_name,
        messages=[{"role": "user", "content": prompt}],
        stop="<END>",
    )
    t = res.choices[0].message.content
    if t is None:
        return ""
    return t


async def async_chat(prompt: str) -> str:
    res = await async_client.chat.completions.create(
        model=CHAT_LLM.model_name,
        messages=[{"role": "user", "content": prompt}],
        stop="<END>",
    )
    t = res.choices[0].message.content
    if t is None:
        return ""
    return t


def generate(prompt: str) -> str:
    if CHAT_LLM.generate:
        return complete(prompt)
    else:
        return chat(prompt)


async def async_generate(prompt: str) -> str:
    if CHAT_LLM.generate:
        return await async_complete(prompt)
    else:
        return await async_chat(prompt)


if __name__ == "__main__":
    question = "讲个故事"
    print(generate(question))
