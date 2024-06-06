from asgiref import sync
import asyncio, aiohttp
import requests
from fake_useragent import UserAgent

# used to get multiple requests url pages data fast
def async_aiohttp_get_all(urls, callback, json = False):
        """
        performs asynchronous get requests
        """
        async def get_all(urls):
            headers = {'User-Agent': UserAgent().random}
            async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(limit=100)) as session:
                async def fetch(url, index):
                    async with session.get(url) as response:
                        content = None
                        if not json:
                            content = await response.text()
                        else:
                            content = await response.json()
                        return callback(content, url, index)
                return await asyncio.gather(*[
                    fetch(url, index) for index, url in enumerate(urls)
                ])
        # call get_all as a sync function to be used in a sync context
        return sync.async_to_sync(get_all)(urls)

def async_aiohttp_get_all_text_only(urls, json = False):
        """
        performs asynchronous get requests
        """
        async def get_all(urls):
            headers = {'User-Agent': UserAgent().random}
            async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(limit=100)) as session:
                async def fetch(url, index):
                    async with session.get(url) as response:
                        content = None
                        if not json:
                            content = await response.text()
                        else:
                            content = await response.json()
                        return content
                return await asyncio.gather(*[
                    fetch(url, index) for index, url in enumerate(urls)
                ])
        # call get_all as a sync function to be used in a sync context
        return sync.async_to_sync(get_all)(urls)
    
# used to get multiple requests url pages data fast
def async_get_all_json_data(urls, json=True):
        """
        performs asynchronous get requests
        """
        async def get_all(urls):
            headers = {'User-Agent': UserAgent().random}
            async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(limit=1000)) as session:
                async def fetch(url, index):
                    async with session.get(url) as response:
                        page_json = await response.json()
                        return page_json
                return await asyncio.gather(*[
                    fetch(url, index) for index, url in enumerate(urls)
                ])
        # call get_all as a sync function to be used in a sync context
        return sync.async_to_sync(get_all)(urls)

def get_response(url: str, json = True):
        headers = {'User-Agent': UserAgent().random}
        response = requests.get(url, headers=headers)
        # getting all matches json data
        if json:
            return  response.json()
        else: 
            return response.text