import uvicorn
uvicorn.run("server:app", host="127.0.0.1", port=9000, reload=True)