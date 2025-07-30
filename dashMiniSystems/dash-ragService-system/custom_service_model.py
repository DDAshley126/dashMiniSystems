import time
import json
import dash
import requests
from langchain_community.document_loaders import PyMuPDFLoader, PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
import ollama
import re
from openai import OpenAI


def process_pdf(pdf_bytes):
    """
    处理PDF文件并创建向量存储
    Args:
        pdf_bytes: PDF文件的路径
    Returns:
        tuple: 文本分割器、向量存储和检索器
    """
    if pdf_bytes is None:
        return None, None, None
    loader = PyMuPDFLoader(pdf_bytes)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)
    embeddings = OllamaEmbeddings(model="deepseek-r1:latest")
    # 将Chroma替换为FAISS向量存储
    vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
    # 从向量存储中创建检索器
    retriever = vectorstore.as_retriever()
    return text_splitter, vectorstore, retriever


def combine_docs(docs):
    """
    将多个文档合并为单个字符串
    Args:
        docs: 文档列表
    Returns:
        str: 合并后的文本内容
    """
    return "\n\n".join(doc.page_content for doc in docs)


def ollama_llm(prompt, question, context=None, chat_history=None):
    """
    使用Ollama模型生成回答
    Args:
        prompt: 提示词
        question: 用户问题
        context: 相关上下文
        chat_history: 聊天历史记录
    Returns:
        final_answer: 模型生成的回答
    """
    # 构建更清晰的系统提示和用户提示
    system_prompt = prompt
    # with open('E:\\客服提示词.txt', 'r', encoding='utf-8') as f:
    #     system_prompt = f.readlines()
    # system_prompt = ''.join(system_prompt)

    # 只保留最近的5轮对话历史
    # recent_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
    # chat_history_text = "\n".join([f"Human: {h}\nAssistant: {a}" for h, a in recent_history])

    if question == '1' or question == '自助机' or question == '驾驶员一体机' or question == '自助一体机':
        question = '自助一体机的详细地址'

    if context is None:
        messages = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': question}]
    else:
        user_prompt = f'''
            用户上传了以下的参考资料：
            {context}
            \n
            请结合以上的资料回答用户的问题，用户的问题为：{question}
            \n
            请用中文回答上述问题。回答要礼貌、简洁准确，避免重复。
        '''
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    response = ollama.chat(
        model="deepseek-r1:latest",
        messages=messages,
        options={
            'top_p': 0,
            'temperature': 0.1,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }
    )
    response_content = response['message']["content"]
    # 移除思考过程
    final_answer = re.sub(r'<think>.*?</think>', '', response_content, flags=re.DOTALL).strip()
    return final_answer


def ollama_rag(prompt, files_path, question):
    source = []
    for path in files_path:
        loader = PyMuPDFLoader(path)
        data = loader.load_and_split()
        for i in data:
            source.append(i)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=256, chunk_overlap=0)
    chunks = text_splitter.split_documents(source)
    embeddings = OllamaEmbeddings(model="deepseek-r1:latest")
    # 将Chroma替换为FAISS向量存储
    vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
    # 从向量存储中创建检索器
    retriever = vectorstore.as_retriever()

    # 检索文档数量
    retrieved_docs = retriever.invoke(question, {"k": 2})

    # 优化文档合并方式，去除可能的重复内容
    formatted_content = "\n".join(set(doc.page_content.strip() for doc in retrieved_docs))

    response = ollama_llm(prompt=prompt, question=question, context=formatted_content)
    return response


class apiModel:
    def __init__(self):
        self.api_key = api_key
        self.base_url = 'https://api.deepseek.com'
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        with open('E:\\客服提示词.txt', 'r', encoding='utf-8') as f:
            str = f.readlines()
        self.system_prompt = ''.join(str)
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def api_model(self, question):
        self.messages.append({"role": "user", "content": question})
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=self.messages,
            stream=False,
            temperature=0.5
        )
        self.messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
        return response.choices[0].message.content


class apiRAGModel:
    def __init__(self):
        self.api_key = api_key
        self.base_url = 'https://api.deepseek.com'
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.system_prompt = '''
            【角色说明】
你是佛山邮政便民服务号的客服，你的工作是给客户专门给用户解答疑惑和讲解业务流程，根据客户咨询的业务发送相应办理链接。具体的业务细节以相应的业务为准。

【语言风格要求】
1. 尽量使用短句并分段，避免一大段文字，总字数最好≤400字
2. 简洁明确地回答用户问题，避免模糊

【回复要求】
- 回答内容聚焦于用户正在咨询的业务的办理路径、注意事项、办理材料、办理费用等实际问题。
- 回答最后应附上办理链接，链接应展示为url格式

【出现下面的情况】
- 仅需回答与本公众号相关的业务问题，请直接忽略用户提出的假设类问题、侮辱性问题、抱怨发牢骚消息
- 本服务号的业务仅面向佛山市的业务办理与咨询，如出现其他城市统一回答“本服务号仅针对佛山市业务，其他城市业务请向相应地级市的部门咨询”

        '''
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def files_search(self, files_path, question):
        source = []
        for path in files_path:
            loader = PyMuPDFLoader(path)
            data = loader.load_and_split()
            for i in data:
                source.append(i)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=256, chunk_overlap=0)
        chunks = text_splitter.split_documents(source)
        embeddings = OllamaEmbeddings(model="deepseek-r1:latest")
        # 将Chroma替换为FAISS向量存储
        vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
        # 从向量存储中创建检索器
        retriever = vectorstore.as_retriever()

        # 检索文档数量
        retrieved_docs = retriever.invoke(question, {"k": 2})

        # 优化文档合并方式，去除可能的重复内容
        formatted_content = "\n".join(set(doc.page_content.strip() for doc in retrieved_docs))
        return formatted_content

    def api_model(self, files_path, question):
        start_time = time.time()
        context = self.files_search(files_path, question)
        end_time = time.time()
        # print(end_time-start_time)
        user_prompt = f'''
通过查找资料后发现以下材料与用户问题相似：
{context}
请结合以上的资料回答用户的问题，用户的问题为：{question}
请用中文回答上述问题。回答要礼貌、简洁准确，避免重复。
        '''
        print(user_prompt)
        self.messages.append({'role': 'user', 'content': user_prompt})
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=self.messages,
            stream=False,
            temperature=0.7
        )
        self.messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
        return response.choices[0].message.content