import os
from dotenv import load_dotenv
from langchain_core.language_models import BaseLanguageModel
from typing import List, Optional, Mapping, Any
from pathlib import Path
import json
from datetime import datetime, timezone
import random


load_dotenv()