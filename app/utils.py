from dataclasses import dataclass
import os
import re
import csv
from pydantic import BaseModel, Field
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings import OpenAIEmbedding
from llama_index.llms import OpenAI
from llama_index.schema import Document
from llama_index.query_engine import CitationQueryEngine
from llama_index.node_parser import SentenceSplitter
from llama_index import (
    VectorStoreIndex,
    ServiceContext,
    StorageContext,
    Document
)

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

class DocumentService:
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

    def __init__(self, input_foldername: str, output_foldername: str):
        self.input_foldername = input_foldername
        self.output_foldername = output_foldername
        self.textract_foldername = "textract_docs/laws"

    def parse_textract(self):
        regex = re.compile(r'\d+(\.\d+)*\.', re.MULTILINE)

        filename = os.path.join(self.textract_foldername, "layout.csv")
        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            texts = []
            for row in spamreader:
                text = row[2]
                if text:
                    matches = regex.finditer(text)
                    section = ""
                    for match in matches:
                        section = match.group()
                        break
                    
                texts.append(Document(metadata={"Section" : section, "filename" : filename}, text=text))
            return texts

    

    def convert_pdf_to_text(self, input_filepath):
        output_filename = "{}.txt".format(input_filepath)
        output_filepath = os.path.join(self.output_foldername, output_filename)
        os.system("java -jar tika-app-2.9.1.jar -T {} > {}".format(input_filepath, output_filepath))
        return output_filename

    def split_text_with_regex(self, input_text):
        # Define the regular expression for citation matching
        regex = re.compile(r'\d+(\.\d+)*\.', re.MULTILINE)
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
            result.append(section)

            # Update the previous end position and enumeration tag
            prev_enumeration = match.group()
            prev_end = end

        # Handle text after the last match
        if prev_end < len(input_text):
            text_after_last_match = input_text[prev_end:].strip()
            result.append({'enumeration': None, 'text': text_after_last_match})

        return result

    def create_documents(self, parse_files: bool = True):
        docs = []
        for filename in os.listdir(self.input_foldername):
            # Convert pdfs to text
            if parse_files:
                input_filepath = os.path.join(self.input_foldername, filename)
                self.convert_pdf_to_text(input_filepath)

            # Create the text file path
            text_filename = "../text_docs/{}.txt".format(filename)
            text_filepath = os.path.join(self.output_foldername, text_filename)

            # Read the file into memory
            with open(text_filepath, 'r') as file:
                # Read the file into memory
                content = file.read()

                # Split the text into sections
                for s in self.split_text_with_regex(content):
                    # Map the section to a Document object
                    document_object = Document(metadata={"Section" : s['enumeration'], "filename" : filename}, text=s['text'])

                    # Add it to the list of documents
                    docs.append(document_object)
        return docs

class QdrantService:
    def __init__(self, k: int = 2):
        self.index = None
        self.k = k
        self.citation_chunk_size = 512

    def connect(self) -> None:
        self.client = qdrant_client.QdrantClient(location=":memory:")
        vstore = QdrantVectorStore(client=self.client, collection_name='temp')

        self.service_context = ServiceContext.from_defaults(
            embed_model=OpenAIEmbedding(),
            llm=OpenAI(api_key=key, model="gpt-4", temperature=0)
            )

        self.storage_context = StorageContext.from_defaults(vector_store=vstore)

    def load(self, docs = 'list[Document]'):
        parser = SentenceSplitter()
        nodes = parser.get_nodes_from_documents(docs)
        self.index = VectorStoreIndex(nodes, storage_context=self.storage_context, service_context=self.service_context)
    
    def query(self, query_str: str) -> Output:
        """
        This method needs to initialize the query engine, run the query, and return
        the result as a pydantic Output class. This is what will be returned as
        JSON via the FastAPI endpount. Fee free to do this however you'd like, but
        a its worth noting that the llama-index package has a CitationQueryEngine...

        Also, be sure to make use of self.k (the number of vectors to return based
        on semantic similarity).

        # Example output object
        citations = [
            Citation(source="Law 1", text="Theft is punishable by hanging"),
            Citation(source="Law 2", text="Tax evasion is punishable by banishment."),
        ]

        output = Output(
            query=query_str, 
            response=response_text, 
            citations=citations
            )
        
        return output

        """

        ## Use the new add method
        query_engine = CitationQueryEngine.from_args(
            self.index,
            similarity_top_k=self.k,
            # here we can control how granular citation sources are, the default is 512
            citation_chunk_size=self.citation_chunk_size,
        )
        response = query_engine.query(query_str)
        citations = []
        for n in response.source_nodes:
            source = n.metadata["Section"]
            text = n.node.get_text()
            citation = Citation(source=source, text=text)
            citations.append(citation)  

        return Output(
            query=query_str, 
            response=response.response, 
            citations=citations
        )

if __name__ == "__main__":
    # # # Example workflow
    doc_serivce = DocumentService("./docs/", "./text_docs") # implemented
    docs = doc_serivce.create_documents(parse_files=False) # implemented
    # docs = doc_serivce.parse_textract()
    index = QdrantService(k=3) # implemented
    index.connect() # implemented
    index.load(docs) # implemented

    output = index.query("what happens if I steal?") # NOT implemented
    print(output)




