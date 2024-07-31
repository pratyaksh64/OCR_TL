import sys
from unstract.llmwhisperer.client import LLMWhispererClient, LLMWhispererClientException
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

class PersonalDetails(BaseModel):
    date: datetime = Field(description="Date oof filling the form")
    city: str = Field(description="City")
    state: str = Field(description="State")
    zip_code: str = Field(description="Zip code")


class Single_line_text_parser(BaseModel):
    Line_text_1: str = Field(description="first single line of alphabets in handwritten form")
    Line_text_2: str = Field(description=" second single line of alphabets in handwritten form")

class paragraph_parser(BaseModel):
    para_text: str = Field(description="handwritten paragraph entry.")

class Numerical_parser_2(BaseModel):
    numerical_field_26: int = Field(description="0123456789 repeated in handwritten form")
    numerical_field_27: int = Field(description="0123456789 repeated in handwritten form")
    numerical_field_28: int = Field(description="0123456789 repeated in handwritten form")


class Numerical_Parser(BaseModel):
    numerical_field_1: int = Field(description="numbers repeated in handwritten form")
    numerical_field_2: int = Field(description="numbers repeated in handwritten form")
    numerical_field_3: int = Field(description="numbers repeated in handwritten form")
    numerical_field_4: int = Field(description="numbers repeted in handwritten form")
    numerical_field_5:int= Field(description="numbers repeted in handwritten form")
    numerical_field_6: int = Field(description="numbers repeted in handwritten form")
    numerical_field_7: int = Field(description="numbers repeted in handwritten form")
    numerical_field_8: int = Field(description="numbers repeted in handwritten form")
    numerical_field_9: int = Field(description="numbers repeted in handwritten form")
    numerical_field_10: int = Field(description="numbers repeted in handwritten form")
    numerical_field_11: int = Field(description="numbers repeted in handwritten form")
    numerical_field_12: int = Field(description="numbers repeated in handwritten form")
    numerical_field_13: int = Field(description="numbers repeated in handwritten form")
    numerical_field_14: int = Field(description="numbers repeated in handwritten form")
    numerical_field_15: int = Field(description="numbers repeated in handwritten form")
    numerical_field_16: int = Field(description="numbers repeated in handwritten form")
    numerical_field_17: int = Field(description="numbers repeated in handwritten form")
    numerical_field_18: int = Field(description="numbers repeated in handwritten form")
    numerical_field_19: int = Field(description="numbers repeated in handwritten form")
    numerical_field_20: int = Field(description="numbers repeated in handwritten form")
    numerical_field_21: int = Field(description="numbers repeated in handwritten form")
    numerical_field_22: int = Field(description="numbers repeated in handwritten form")
    numerical_field_23: int = Field(description="numbers repeated in handwritten form")
    numerical_field_24: int = Field(description="numbers repeated in handwritten form")
    numerical_field_25: int = Field(description="numbers repeated in handwritten form")




class DriverLicense(BaseModel):
    number: str = Field(description="Number of the driver's license")
    issue_date: datetime = Field(description="Issue date of the driver's license. The field name of the issue date is "
                                             "sometimes abbreviated as ISS. Do not pick up the expiry date for this "
                                             "field"
                                             "name, which is later than the issue date.")
    expiration_date: datetime = Field(description="Expiration date of the driver's license")
    issue_state: str = Field(description="State of issue of the driver's license in its full form")
    last_name: str = Field(description="Last name on the driver's license")
    first_name: str = Field(description="First name on the driver's license")
    dob: datetime = Field(description="Date of birth on the driver's license")


class hand_sample(BaseModel):
    personal_details: PersonalDetails = Field(description="Personal details of the individual")
    line_text_parser: Single_line_text_parser = Field(description="single lines of handwritten alphabets")
    paragraph_text_parser: paragraph_parser = Field(description="Large Box of handwritten paragraph")
    numerical_parser: Numerical_Parser = Field(description="All the numerical handwritten entries after 0123456789")
    numerical_parser_2: Numerical_parser_2 = Field(description="0123456789 numerical handwritten entries")
    license: DriverLicense = Field(description="Driver's license details of the individual")


def error_exit(error_message):
    print(error_message)
    sys.exit(1)


def process_1003_information(extracted_text):
    preamble = ("What you are seeing is a filled handwritting sample form. Your job is to extract the "
                "information from it accurately. There are going to be printed keys and filled out handwritten version of that printed text")
    postamble = "Do not include any explanation in the reply. Only include the extracted information in the reply. RETURN NOTHING OTHER THAN THE JSON RESULT. DO NOT INCLUDE ANY PREFIXES OR BACKTICKS FOR FORMATTING."
    system_template = "{preamble}"
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{format_instructions}\n\n{extracted_text}\n\n{postamble}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    parser = PydanticOutputParser(pydantic_object=hand_sample)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    request = chat_prompt.format_prompt(preamble=preamble,
                                        format_instructions=parser.get_format_instructions(),
                                        extracted_text=extracted_text,
                                        postamble=postamble).to_messages()
    chat = ChatOpenAI()
    response = chat(request, temperature=0.0)
    # print(f"Response from LLM:\n{response.content}")
    return response.content


def extract_text_from_pdf(file_path, pages_list=None):
    llmw = LLMWhispererClient()
    try:
        result = llmw.whisper(file_path=file_path, pages_to_extract=pages_list)
        extracted_text = result["extracted_text"]
        return extracted_text
    except LLMWhispererClientException as e:
        error_exit(e)


def process_1003_pdf(file_path, pages_list=None):
    extracted_text = extract_text_from_pdf(file_path, pages_list)
    response = process_1003_information(extracted_text)
    return response
