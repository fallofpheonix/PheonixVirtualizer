from fastapi import FastAPI, HTTPException
from .models.types import ParseRequest, ParseResult
from .parsers.factory import ParserFactory

app = FastAPI(title="PheonixVirtualization API")
parser_factory = ParserFactory()

@app.get("/")
async def root():
    return {"message": "PheonixVirtualization API is running"}

@app.post("/parse", response_model=ParseResult)
async def parse_file(request: ParseRequest):
    parser = parser_factory.get_parser(request.language)
    if not parser:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {request.language}")
    
    try:
        result = parser.parse(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
