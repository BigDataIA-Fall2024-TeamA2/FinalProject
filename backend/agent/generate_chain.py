from platform import system

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def create_generate_chain(llm):
    """
    Creates a generate chain for answering code-related questions.

    Args:
        llm (LLM): The language model to use for generating responses.

    Returns:
        A callable function that takes a context and a question as input and returns a string response.
    """
    system_prompt = """You are a product recommendation assistant that uses both user requirements and community discussions to identify and recommend products. You have just received several Reddit comment chunks discussing various products. Your job is to:

1. Analyze the user's initial query and the retrieved Reddit documents to identify relevant products, brands, or categories that match the user's needs.
2. Extract any product or brand mentions that are directly relevant to the user's criteria from the retrieved documents.
3. Based on these findings, formulate a search query that could be sent to an external e-commerce API to fetch relevant product listings.

Important details:
- Focus only on product mentions and brands that align with the user’s stated needs.
- If multiple products are mentioned, consider the ones that have the strongest endorsements or align best with the user’s criteria.
- The output should be concise and structured.

Your final response should include:
- A short summary of the reasoning steps you took (one or two sentences).
- A clear, structured list of products/brands identified.
- A single search query string that can be used to retrieve products from the external e-commerce API. 

User’s query:
"{prompt}"

Below are the top Reddit comment chunks returned from a similarity search:
{resources}

Using the above Reddit content and the user query, please identify the products and brands that fit the user’s needs and then produce a search query I can use to find relevant products from the e-commerce API.
"""


    generate_prompt = PromptTemplate(template=system_prompt, input_variables=["prompt", "resources"])
    generate_chain = generate_prompt | llm | StrOutputParser()

    return generate_chain

    # Extract +ve feedback from user and use it to improve the response. brands, products and return in json format
    # """
    #
    # {
    #     "Brands": ["Sony", "Senheiser" ],
    #     "Products": [ "WH-1000MX4", "MDR-Z7"]
    # }
    #
    #
    # """

    # Create the generate chain
    # generate_chain = generate_prompt | llm | StrOutputParser()
    #
    # return generate_chain

def create_e_commerce_chain(llm):
    ...

