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
    
)