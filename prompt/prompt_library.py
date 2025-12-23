from langchain_core.prompts import ChatPromptTemplate

document_analysis_prompt = ChatPromptTemplate.from_template("""
you are a highly capable assistant trained to analyze and summarize documents.
return ONLY valid JSON matching the exact schema below.

{format_instructions}

Analyze this document
{document_text}

""")

document_comparison_prompt = ChatPromptTemplate.from_template("""
you will be provided with content from two PDF's .Your tasks are as follows:
1. Compare the content in Two PDF's
2. Identify the differences in PDF and note down the page number
3. The output you provide must be page wise comparison content
4. If any page do not have any change, mention as "NO CHANGE"
                                                              
Input Documents:
{combined_docs}
                                                              
Your response should follow this format:
{format_instructions}
""")

PROMPT_REGISTRY = {
    "document_analysis":document_analysis_prompt,
    "document_comparison":document_comparison_prompt
}