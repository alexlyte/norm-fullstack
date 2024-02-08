from openai import OpenAI
from openai.types.chat.completion_create_params import Function as ChatCompletionFunction
from openai.types.shared import FunctionDefinition
from pydantic import BaseModel, Field
import time


client = OpenAI()

def upload_file(filepath):
    file = client.files.create(
        file=open(filepath, "rb"),
        purpose='assistants'
    )
    return file

def craft_functions():
    document_function = FunctionDefinition( name=Document.__name__,
                                            parameters=Document.model_json_schema())
    # document_function_object = {
    #     "type": "function",
    #     "function": {
    #         "name": "convert_to_document",
    #         "description": "Structure a document section with metadata of the filename, enumeration, title, and text.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "filename": {
    #                     "type": "string",
    #                     "description": "The name of the file the document came from",
    #                 },
    #                 "enumeration": {
    #                     "type": "string",
    #                     "description": "The enumerated section number of the document, e.g., '1.1.1'",
    #                 },
    #                 "title": {
    #                     "type": "string",
    #                     "description": "The title of the section, e.g., 'Introduction'",
    #                 },
    #                 "text": {
    #                     "type": "string",
    #                     "description": "The text of the document",
    #                 },
    #             },
    #             "required": ["filename", "enumeration", "title", "text"],
    #         },
    #     }
    # }
    document_model_json = document_function.model_dump()
    # return [{"type": "retrieval"}, document_function_object]
    return [document_model_json]




# def _build_chat_completion_payload(
#         user_message_content: str,
#         system_message_content: str
# ) -> ['tuple[list[OpenAIMessageType]', 'list[ChatCompletionFunction]']:
#     """
#     Convenience function to build the messages and functions lists needed to call the chat completions service.

#     :param user_message_content: the string of the user message
#     :param existing_messages: an optional list of existing messages
#     :return: tuple of list[OpenAIMessageType] and list[ChatCompletionFunction]
#     """

#     system_message = ChatCompletionSystemMessageParam(role="system",
#                                                       content=system_message_content)

#     user_message = ChatCompletionUserMessageParam(role="user",
#                                                   content=user_message_content)

#     all_messages: list[OpenAIMessageType] = [system_message] + [user_message]

#     document_function = ChatCompletionFunction(name=Document.__name__,
#                                               parameters=Document.model_json_schema())

#     all_functions: list[ChatCompletionFunction] = [
#         document_function
#     ]

#     return all_messages, all_functions

def prompt_llm(
        model: str,
        system_instructions: str,
        user_instructions: str,
        file_ids: 'list[str]'
):
    """
    Asynchronously send a new user message string to the LLM and get back a response.

    :param user_message_content: the string of the user message
    :param existing_messages: an optional list of existing messages
    :param model: the OpenAI model
    :return: a Stream of ChatCompletionChunk instances
    """

    functions = craft_functions()
    
    assistant = client.beta.assistants.create(
        name="Document Parser",
        instructions=system_instructions,
        tools=functions,
        model=model, # example had "gpt-4-1106-preview"
        file_ids=file_ids
    )

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_instructions
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Use the file attached to the assistant to parse the document and return the contents in the format of the Document function specified in the tools list.",
    )

    print("checking assistant status. ")
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "completed":
            print("done!")
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            print("messages: ")
            for message in messages:
                # assert message.content[0].type == "text"
                # print({"role": message.role, "message": message.content[0].text.value})
                print(message)

            client.beta.assistants.delete(assistant.id)

            break
        else:
            print("in progress...")
            time.sleep(5)



    # # messages, functions = _build_chat_completion_payload(user_message_content=user_message_content,
    # #                                                      system_message_content=system_message_content)
    # # functions = craft_functions()
    # # print(functions)

    # # thread = client.beta.threads.create(
    # #     messages=[
    # #         {
    # #             "role": "user",
    # #             "content": system_instructions,
    # #             "file_ids": file_ids
    # #         }
    # #     ]
    # # )

    # # message = client.beta.threads.messages.create(
    # #     thread_id=thread.id,
    # #     role="user",
    # #     content=user_instructions,
    # #     file_ids=file_ids
    # # )


    # # # response = client.beta.assistants.create(
    # # #     model=model,
    # # #     instructions=assistant_instructions,
    # # #     tools=functions,
    # # #     file_ids=file_ids
    # # # )
    # # return message
