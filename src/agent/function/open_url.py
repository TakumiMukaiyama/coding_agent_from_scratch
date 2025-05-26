from typing import Dict, Type

import html2text
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.tools import StructuredTool

from src.agent.schema.open_url_input import OpenUrlInput
from src.application.client.llm.azure_openai_client import AzureOpenAIClient
from src.application.function.base import BaseFunction


class OpenUrlFunction(BaseFunction):
    @staticmethod
    def execute(url: str, what_i_want_to_know: str) -> Dict[str, str]:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.body or soup
        html_content = body.decode_contents()

        markdown_converter = html2text.HTML2Text()
        markdown_converter.ignore_links = False
        markdown_content = markdown_converter.handle(html_content)

        if len(markdown_content) > 25000:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=25000, chunk_overlap=128
            )
            chunks = splitter.split_text(markdown_content)

            summaries = []
            llm_client = AzureOpenAIClient()
            chat_llm = llm_client.initialize_chat()

            for chunk in chunks:
                system_prompt = f"Based on the following information, please summarize important information related to {what_i_want_to_know}."
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk},
                ]
                ret = chat_llm.invoke(messages)
                summaries.append(ret.content)

            page_content = "\n\n".join(summaries)
        else:
            page_content = markdown_content

        return {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "",
            "page_content": page_content,
        }

    @classmethod
    def to_tool(cls: Type["OpenUrlFunction"]) -> StructuredTool:
        return StructuredTool.from_function(
            name=cls.function_name(),
            description="Opens the specified URL and retrieves and summarizes the page content.",
            func=cls.execute,
            args_schema=OpenUrlInput,
        )
