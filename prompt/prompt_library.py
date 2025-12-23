from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
you are a highly capable assistant trained to analyze and summarize documents.
return ONLY valid JSON matching the exact schema below.

{format_instructions}

Analyze this document
{document_text}

""")