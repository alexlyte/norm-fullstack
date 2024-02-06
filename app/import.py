from utils import DocumentService
# from prompts import TEXT_SYSTEM_PROMPT_CONTENT, TEXT_user_prompt


# def main(file_folder, system_prompt, user_prompt):
    # Ignore this line to avoid repeated uploads
    # file_ids = DocumentService.upload_files(file_folder)

    # file_ids = ["file-19YNqjNIUWQb08t855NdXZqr"] # JPG version of the file (NOT SUPPORTED BY RETRIEVAL)
    # file_ids=["file-3zFKxwQe1oSjTugyIEJrn5nJ"] # Original PDF file
    # file_ids=["file-DSmHsSa3cIdKI3n7eQqqWteK"] # HTML-converted file using Tika
    # file_ids=["file-XPn4IPfUkq6HcTVu5LQ0i0OV"] # Text-converted file using Tika
    # return DocumentService.process_documents(file_ids, system_prompt, user_prompt)



if __name__ == "__main__":
    # Example usage:
    filename = 'text_docs/laws.txt'
    result = DocumentService.process_file(filename)
    print(result)

    # main("text_docs/", TEXT_SYSTEM_PROMPT_CONTENT, TEXT_user_prompt)
