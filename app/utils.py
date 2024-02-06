from dataclasses import dataclass
import os
import re
from pydantic import BaseModel, Field
# import qdrant_client
# from llama_index.vector_stores.qdrant import QdrantVectorStore
# from llama_index.embeddings import OpenAIEmbedding
# from llama_index.llms import OpenAI
# from llama_index.schema import Document
# from llama_index import (
#     VectorStoreIndex,
#     ServiceContext,
# )
# from llm import prompt_llm, upload_file

key = os.environ['OPENAI_API_KEY']


@dataclass
class Input:
    query: str
    file_path: str

@dataclass
class Citation:
    source: str
    text: str

class Output(BaseModel):
    query: str
    response: str
    citations: 'list[Citation]'


def split_text_with_regex(input_text, regex):
    matches = regex.finditer(input_text)

    result = []
    prev_end = 0
    prev_enumeration = ""

    for match in matches:
        start, end = match.start(), match.end()
        text_between = input_text[prev_end:start].strip()

        # Create JSON object
        section = {
            'enumeration': prev_enumeration,
            'text': text_between
        }
        prev_enumeration = match.group()
        print(section)
        result.append(section)

        # Update the previous end position
        prev_end = end

    # Handle text after the last match
    if prev_end < len(input_text):
        text_after_last_match = input_text[prev_end:].strip()
        result.append({'enumeration': None, 'text': text_after_last_match})

    return result


class DocumentService:
    # def upload_files(folder_path):
    #     # ignoring this for now to avoid repeated uploads
    #     files = [os.path.join(folder_path, filepath) for filepath in os.listdir(folder_path)]
    #     file_ids = [upload_file(filename) for filename in files]
    #     return file_ids


    def create_documents(self, filename):
        # Define the regular expression
        regex_pattern = re.compile(r'\d+(\.\d+)*\.', re.MULTILINE)

        # Read the file into memory
        with open(filename, 'r') as file:
            content = file.read()

        # Split the text into sections
        sections = split_text_with_regex(content, regex_pattern)
        # for s in sections:
        #     print(s)
        # return lines


    # def process_documents(file_ids, system_prompt, user_prompt):
        # prompt_llm(
        #     system_instructions=system_prompt,
        #     user_instructions=user_prompt,
        #     model="gpt-4-turbo-preview",
        #     file_ids=file_ids
        # )

        # print(response) 


        # messages=[
        #     {
        #         "role": "system",
        #         "content": SYSTEM_PROMPT_CONTENT
        #     },
        #     {
        #         "role": "user",
        #         "content": "Please parse the attached PDF and return the contents in the format of the Document function specified in the tools list.",
        #     }
        # ]
 


 
        # # Add the file to the assistant
        # assistant = client.beta.assistants.create(
        #     instructions=SYSTEM_PROMPT_CONTENT,
        #     model="gpt-4-turbo-preview",
        #     tools=[{"type": "retrieval"}],
        #     file_ids=[file.id]
        # )
        # print(assistant)
        # message = client.beta.threads.messages.create(
        #     thread_id=thread.id,
        #     role="user",
        #     content="I can not find in the PDF manual how to turn off this device.",
        #     file_ids=[file.id]
        # )


    """
    Update this service to load the pdf and extract its contents.
    The example code below will help with the data structured required
    when using the QdrantService.load() method below. Note: for this
    exercise, ignore the subtle difference between llama-index's 
    Document and Node classes (i.e, treat them as interchangeable).

    # example code
    def create_documents() -> list[Document]:

        docs = [
            Document(
                metadata={"Section": "Law 1"},
                text="Theft is punishable by hanging",
            ),
            Document(
                metadata={"Section": "Law 2"},
                text="Tax evasion is punishable by banishment.",
            ),
        ]

        return docs

     """

# class QdrantService:
#     def __init__(self, k: int = 2):
#         self.index = None
#         self.k = k
    
#     def connect(self) -> None:
#         client = qdrant_client.QdrantClient(location=":memory:")
                
#         vstore = QdrantVectorStore(client=client, collection_name='temp')

#         service_context = ServiceContext.from_defaults(
#             embed_model=OpenAIEmbedding(),
#             llm=OpenAI(api_key=key, model="gpt-4")
#             )

#         self.index = VectorStoreIndex.from_vector_store(
#             vector_store=vstore, 
#             service_context=service_context
#             )

#     def load(self, docs = list[Document]):
#         self.index.insert_nodes(docs)
    
#     def query(self, query_str: str) -> Output:

#         """
#         This method needs to initialize the query engine, run the query, and return
#         the result as a pydantic Output class. This is what will be returned as
#         JSON via the FastAPI endpount. Fee free to do this however you'd like, but
#         a its worth noting that the llama-index package has a CitationQueryEngine...

#         Also, be sure to make use of self.k (the number of vectors to return based
#         on semantic similarity).

#         # Example output object
#         citations = [
#             Citation(source="Law 1", text="Theft is punishable by hanging"),
#             Citation(source="Law 2", text="Tax evasion is punishable by banishment."),
#         ]

#         output = Output(
#             query=query_str, 
#             response=response_text, 
#             citations=citations
#             )
        
#         return output

#         """
       

if __name__ == "__main__":
    # Example workflow
    filename = 'text_docs/laws.txt'
    doc_serivce = DocumentService() # implemented
    docs = doc_serivce.create_documents(filename) # NOT implemented
    # for d in docs:
    #     print(d)
    # index = QdrantService() # implemented
    # index.connect() # implemented
    # index.load() # implemented

    # index.query("what happens if I steal?") # NOT implemented





