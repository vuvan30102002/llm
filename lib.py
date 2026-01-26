import os
from dotenv import load_dotenv
from langchain_core.language_models import BaseLanguageModel
from typing import List, Optional, Mapping, Any
from pathlib import Path
import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import random


load_dotenv()