"""http服务入口"""
import nest_asyncio

nest_asyncio.apply()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='app:create_app', host='127.0.0.1', port=9000, reload=True, debug=True)
