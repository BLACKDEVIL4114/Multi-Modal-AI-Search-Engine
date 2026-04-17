import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add app to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from streamlit_app import perform_web_search, scrape_url, call_bedrock, call_groq

def test_web_search_logic():
    with patch('streamlit_app.DDGS') as mock_ddgs:
        mock_instance = mock_ddgs.return_value.__enter__.return_value
        mock_instance.text.return_value = [{'href': 'http://test.com', 'body': 'IPL results'}]
        mock_instance.news.return_value = [{'title': 'Match Update', 'body': 'KKR won', 'url': 'http://news.com'}]
        
        result = perform_web_search("ipl match")
        assert "IPL results" in result
        assert "KKR won" in result

def test_scraping_logic():
    with patch('trafilatura.fetch_url') as mock_fetch:
        with patch('trafilatura.extract') as mock_extract:
            mock_fetch.return_value = "raw_html"
            mock_extract.return_value = "Cleaned Content"
            
            result = scrape_url("http://test.com")
            assert result == "Cleaned Content"

def test_intelligence_routing_fallback():
    with patch('requests.post') as mock_post:
        # Mock AWS Bedrock Quota Error (429)
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response
        
        with patch('streamlit_app.call_groq') as mock_groq:
            mock_groq.return_value = "Groq Fallback Answer"
            
            result = call_bedrock("Hello")
            assert result == "Groq Fallback Answer"
            mock_groq.assert_called_once()
