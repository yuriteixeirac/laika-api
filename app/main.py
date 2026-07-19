from typing import Annotated

from langchain_core.messages import BaseMessage
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import BaseModel
from rich import print
from fastapi import FastAPI, File, UploadFile
import aiofiles

from .agent import llm

app = FastAPI(title="Lyla API")

class RequestModel(BaseModel):
    msg: str


class ResponseModel(BaseModel):
    response: str


@app.post("/", response_model=ResponseModel)
async def index(request: RequestModel) -> ResponseModel:
    output = await llm.ainvoke(request.msg)

    if not isinstance(output.content, str):
        return ResponseModel(
            response="desgraca"
        )

    return ResponseModel(
        response=output.content
    )


@app.post("/file")
async def file(request: Annotated[bytes, File()]):
    async with aiofiles

# async def main():
#     messages: list[BaseMessage] = []

#     while True:
#         msg = input("> ")
#         if msg == "/quit":
#             break

#         messages.append(HumanMessage(msg))

#         output: AIMessage = await llm.ainvoke(messages)
#         messages.append(output) # type: ignore

#         if output.tool_calls:
#             for tool_call in output.tool_calls:
#                 content = json.dumps({})
#                 if tool_call["name"] == "get_age":
#                     result = await get_age.ainvoke(tool_call["args"])
#                     content = json.dumps({"age": result})
#                 elif tool_call["name"] == "get_user_name":
#                     result = await get_user_name.ainvoke(tool_call["args"])
#                     content = json.dumps({"name": result})

#                 messages.append(
#                     ToolMessage(
#                         content=content,
#                         tool_call_id=tool_call["id"]
#                     )
#                 )

#             output = await llm.ainvoke(messages)
#             messages.append(output)

#         print(output.content)
