from fastapi import FastAPI
import uvicorn
from typing import Any, Dict, AnyStr, List, Union
from utils import validations, generate_response, store_in_db

app = FastAPI()

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]


@app.post("/identify")
async def root(input_json: JSONStructure = None):
    if validations(input_json):
        resp = store_in_db(input_json)
        if resp != "ok":
            response = {"error": resp}
        else:
            response = generate_response(input_json)
    else:
        response = {"error": "input validations failed"}
    return response


if __name__ == "__main__":
    uvicorn.run("identity_reco:app", reload=True, port=3232)
