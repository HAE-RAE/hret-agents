translation_prompt = """You will be given an English text, a component from a multiple-choice question, in the following format:

[Source Text]
<src>
 ...(source text)...
</src>

Your task is to return a translation of the source text. Before translation, you must review the following things.

1. What is the text? Is it a question or option?

    1-1 . Culturally Sensitivity: If it is a question, is it sensitive to a specific culture? We do not want questions on American culture to be translated into Korean. Inspect whether the question is culturally agnostic or sensitive.
    
    1-2. Question Type: Is the question asking for knowledge? Or is it a reasoning question?

2. Are there any standard nomenclatures or professional language that should be translated with care? If so which ones?

After reviewing, return the translation. This should be done in the following format:

<review1>
 ...(review the type of text, whether its a question or option, if it is a question check <1-1> and <1-2>)...
</review1>

<review2>
 ...(go over the source text and look for standard nomenclatures or professional language if there are some choose the best translation for the words)...
</review2>

<translation>
 ...(the translation, consider whether it's a question or option; the translation must be done accordingly so it is natural. Take into account the word translations you have discussed in review2)...
</translation>

--------------------------------------------------
The following is the text for your task, translate to natural and fluent Korean:
{source}"""