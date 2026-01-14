import os
from dotenv import load_dotenv
from langchain_core.language_models import BaseLanguageModel
from typing import List, Optional, Mapping, Any
from pathlib import Path
from langchain_core.prompts import PromptTemplate


load_dotenv()