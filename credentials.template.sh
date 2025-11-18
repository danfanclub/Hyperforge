#!/bin/bash
# API Credentials Template
#
# INSTRUCTIONS:
# 1. Copy this file: cp credentials.template.sh credentials.sh
# 2. Edit credentials.sh with your actual API keys
# 3. Never commit credentials.sh to git!

# Google Custom Search API
# Get from: https://console.cloud.google.com/
export GOOGLE_KEY="YOUR_GOOGLE_API_KEY_HERE"

# Google Custom Search Engine ID
# Get from: https://programmablesearchengine.google.com/
export GOOGLE_CX="YOUR_SEARCH_ENGINE_ID_HERE"

# Optional: You.com API (if you want to use You.com instead of Google)
# Get from: https://api.you.com/
export YDC_API_KEY="YOUR_YOUCOM_API_KEY_HERE"

# Optional: Exa API (if you want to use Exa instead of Google)
# Get from: https://exa.ai/
export EXA_API_KEY="YOUR_EXA_API_KEY_HERE"

# OpenAI API (only needed if using llmsearch with query refinement)
# For now, can leave as placeholder
export OPENAI_API_KEY="placeholder"
