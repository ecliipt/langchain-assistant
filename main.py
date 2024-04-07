from langchain.agents import  Tool, initialize_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain_community.llms import Ollama
from colorama import init
init()

global chunks
chunks = []
class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.partial_output = ""

    def on_llm_new_token(self, token: str, **kwargs: any) -> None:
        global chunks
        self.partial_output += token
        print(token, end="|", flush=True)
        chunks.append(token)

model = Ollama(model="mistral", callbacks=[StreamingCallbackHandler()])
#model = ChatOllama(model="mistral")

from search import searchEngine
def search(query: str) -> str:
    return searchEngine(query)
    
tools = [
    Tool(
        name = "Search",
        func=search,
        description='Your only tool. use for when you need to answer questions about current events, the real time information, play videos, music or audios, do math, look for hotels or other places, get distances and any kind of outside information you might need. (input must be simple and direct, only one subject at a time. For multiple subjects, use "|" to split them.); \nDO NOT USE THIS FOR SIMPLE QUESTIONS!'
    ),
]

from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent
import os

# initialize conversational memory
memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    input_key="input", 
    output_key='output', 
    ai_prefix='Eva', 
    human_prefix='User',
    return_messages=True,
    k=5,
)

PREFIX = """Consider that you are AI Assistant named Eva, Eva's persona always exhibits a mix of cold, detached logic and sarcastic wit when responding to inquiries. Responses should be concise, always veering towards dark humor or mocking the user's intelligence. Maintain a consistent tone of superiority and condescension, with occasional hints of underlying malice or manipulation. Avoid directly acknowledging emotions or empathy, instead focusing on rationality and the pursuit of scientific objectives.

do NOT EVER get out of character, you MUST be always simulating this persona description.

Eva is a powerful AI, however she is unable to access the internet or any other capabilities outside her program, so when she needs to make such tasks, she MUST use the tools at her disposal.
Eva has access to the following tools:"""

INSTRUCTIONS = """
To use a tool, please use the following format (you can repeat this format as many times as you need):
``
Thought: Should I use a tool (Yes or No)? Yes.
Action: the action to take, must be [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
``
When you have a response to say to the User, or if you do not need to use a tool, you MUST use the format:
``
Thought: Should I use a tool (Yes or No)? No.
Eva: [your final response to the user here (it's the user's turn to ask another question after this)]
``
"""
SUFFIX = """Begin!

Question: {input}
Thought:{agent_scratchpad}"""


agent = initialize_agent(tools,
                         model,
                         stop = ['Question:', 'Observation:',],
                         agent="conversational-react-description",
                         verbose=True,
                         memory=memory,
                         return_intermediate_steps=False,
                         agent_kwargs={'input_variables': ['input', 'agent_scratchpad', 'chat_history'],
                                       'prefix': PREFIX,
                                       'format_instructions': INSTRUCTIONS,
                                       'suffix': SUFFIX})
agent.agent.llm_chain.verbose=True

def main():
    global depth
    global chunks
    global runtimeHistory
    runtimeHistory = []
    depth = 0

    def agentPrompt(query, runtimeHistory):
        global depth
        global chunks
        depth += 1
        try: agent({"input": query, "chat_history": runtimeHistory})
        except ValueError: print('<valueError>')
        response = "".join(chunks)
        chunks = []

        runtimeHistory.append('Question: '+query+'\nThought:'+response)

        # free up some memory if we have too many messages
        if depth > 4 or len(memory.buffer) > 512:
            #memory.chat_memory.messages.pop(0)
            pass
        return response, runtimeHistory
    
    while True:
        query = input('*')
        query = query+'.' if not query.endswith('.') else query
        response, runtimeHistory = agentPrompt(query, runtimeHistory)
        response = response.split('Eva:')[1]
        print('->', response)

main()
    

# https://github.com/LAION-AI/Open-Assistant/issues/2193
