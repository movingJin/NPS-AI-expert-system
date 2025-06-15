from langchain.schema import Document
from typing import List, Literal
from langchain.schema import HumanMessage, SystemMessage
from utils.config import get_llm
from utils.config import get_embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import pdfplumber


def extract_tables_from_pdf(file_path):
    table_texts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                formatted_table = "\n".join([
                    "\t".join([
                        str(cell).replace("\n", " ").strip() if cell is not None else "" 
                        for cell in row
                    ]) for row in table
                ])
                table_texts.append(formatted_table)
    return table_texts


def get_search_chain():
    loader = PyMuPDFLoader("./2025 알기쉬운 국민연금 사업장 실무안내.pdf")
    docs = loader.load()

    table_texts = extract_tables_from_pdf("./2025 알기쉬운 국민연금 사업장 실무안내.pdf")
    table_docs = [Document(page_content=t, metadata={"source": "table"}) for t in table_texts]

    all_docs = docs + table_docs

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    split_documents = text_splitter.split_documents(all_docs)
    embeddings = get_embeddings()

    examples = [
    """
    질문) 현재 나이 35세의 사람의 노령연금 수급연령을 알려줘.
    응답) 국민연금 수급연령은 출생 연도에 따라 다릅니다.
        현재 나이가 35세라면 출생 연도는 2025년 기준으로 계산했을 때 1989년 또는 1990년입니다. 국민연금의 노령연금 수급연령은 출생 연도별로 다음과 같이 정해집니다:

        1953~1956년생: 61세
        1957~1960년생: 62세
        1961~1964년생: 63세
        1965~1968년생: 64세
        1969년생 이후: 65세
        따라서, 1989년 또는 1990년생인 현재 나이 35세의 사람은 65세부터 노령연금을 수급할 수 있습니다.

        출처 및 근거: 
        ~1952년생: 60세
        1953~1956년생: 61세
        1957~1960년생: 62세
        1961~1964년생: 63세
        1965~1968년생: 64세
        1969년생 이후: 65세, 92페이지 참조.
    """,
    """
    질문) 파주지사의 전화번호를 알려줘.
    응답) 요청하신 파주지사의 전화번호: 031-956-3622 FAX번호: 031-303-2226 입니다.
            출처 및 근거: 163페이지 참조.
    """]
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
    retriever = vectorstore.as_retriever()
    prompt = PromptTemplate.from_template(
        """You are a Korean-speaking expert in 국민연금 실무.
        표 형식 데이터도 포함되어 있으며, 표 안의 수치, 조건, 예외사항이 핵심일 수 있습니다.
        문맥에서 표 내용이 있을 경우 이를 우선 고려하여 질문에 답하세요.
        또한, 출처한 내용의 page번호와 핵심내용을 같이 출력해주세요.
        필요시 표 또는 그래프 형태가 출력되어도 좋습니다.
        If you don't know the answer, just say that you don't know. 
        Answer in Korean.
        예시:
        {examples}
        """.format(examples="\n\n".join(examples))
        +
    """
    #Context: 
    {context}

    #Question:
    {question}

    #Answer:"""
    )

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | get_llm()
        | StrOutputParser()
    )

    return vectorstore, chain


def get_next_query(
    answer: str,
) -> List[str]:

    template ="""
    응답내용: 
    {answer}
    에 대해 사용자가 궁금해할만한 관련된 다음 질문을 생성해주세요.
    질문만 제공하고 설명은 하지 마세요.
    출력예시:
    대상자의 조기노령연금의 수급연령을 알려주세요.
    대상자가 장애연금을 기수급 받는 경우, 연금금액이 어떻게 달라지는지 알려주세요. 
    대상자가 사망한 경우, 연금수혜자는 누가되는지 알려주세요.
    """
    prompt = template.format(answer=answer)

    messages = [
        SystemMessage(
            content=
            """
            당신은 국민연금 실무 전문가입니다.
            사용자는 당신으로부터 이미 한 차례 질의에 대한 응답을 받았으며,
            당신의 응답에 대해 사용자가 궁금해할만한 다음 질문을 생성해주세요.
            각 질문은 100자 이내로 작성하고, 각 질문은 반드시 특수문자($$)로 구분하세요.
            추후, 이 질문은 tokenizing 될 것입니다.
            """
        ),
        HumanMessage(content=prompt),
    ]

    response = get_llm().invoke(messages)
    suggested_queries = [q.strip() for q in response.content.split("$$")]
    return suggested_queries[:3]