import os
import json
import asyncio
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from flask import Flask, render_template, redirect, url_for, flash, request
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuild import create_react_agent

load_dotenv()
model = ChatOpenAI(model="gpt-4o")

server_params = StdioServerParameters(
    command='npx',
    args=['@brightdata/mcp'],
    env = {
        'API_TOKEN': os.getenv('API_TOKEN'),
        'BROWSER_AUTH': os.getenv('BROWSER_AUTH'),
        'WEB_UNLOCKER_ZONE': os.getenv('WEB_UNLOCKER_ZONE')
    }
)

SYSTEM_PROMPT = (
    "To find products, first use the search_engine tool. When finding products, use the web_data tool for the platform. If none exists, scrape as markdown."
    "Example: Don't use web_data_bestbuy_products for search. Use it only for getting data on specific products you already found in search."
)

PLATFORMS = ['Amazon', 'Best Buy', 'Ebay', 'Walmart', 'Target', 'Costco', 'Newegg']

class Hit(BaseModel):
    url: str = Field(..., description='The URL of the product that was found')
    title: str = Field(..., description='The title of the product that was found')
    rating: str = Field(..., description='The rating of the product (starts, number of ratings given etc.)')

class PlatformBlock(BaseModel):
    platform: str = Field(..., description='Name of the platform')
    results: list[Hit] = Field(..., description='List of results for this platform')

class ProductSearchResponse(BaseModel):
    platforms: list[PlatformBlock] = Field(..., description='Aggregated list of all results grouped by platform')


app = Flask(__name__)
app.secret_key = 'mysecretkey-not-for-prod'

async def run_agent(query, platforms):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as sess:
            await sess.initialize()

            tools = await load_mcp_tools(sess)

            agent = create_react_agent(model, tools, response_format=ProductSearchResponse)
            
