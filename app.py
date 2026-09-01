import uvicorn

if __name__ == "__main__":
    uvicorn.run("ut2_tfu_proy.main:app", host="0.0.0.0", port=8000)
