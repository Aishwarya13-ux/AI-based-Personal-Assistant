"""
Web Scraping Service for AI Personal Assistant
"""
import requests
import wikipedia
import wolframalpha
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus
from utils.logger import setup_logger, log_error
from config import USER_AGENT, REQUEST_TIMEOUT, WOLFRAM_API_KEY, WEATHER_API_KEY

class WebScraper:
    """Handles web scraping and information retrieval."""
    
    def __init__(self):
        self.logger = setup_logger("web_scraper")
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
        # Initialize Wolfram Alpha client if API key is available
        self.wolfram_client = None
        if WOLFRAM_API_KEY:
            try:
                self.wolfram_client = wolframalpha.Client(WOLFRAM_API_KEY)
                self.logger.info("Wolfram Alpha client initialized")
            except Exception as e:
                log_error(e, "Wolfram Alpha initialization", self.logger)
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web for information.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            List[Dict]: Search results
        """
        results = []
        
        try:
            # Try DuckDuckGo instant answer API
            duckduckgo_results = self._search_duckduckgo(query)
            if duckduckgo_results:
                results.extend(duckduckgo_results[:max_results])
            
            # Try Wikipedia search
            wikipedia_results = self._search_wikipedia(query, max_results)
            if wikipedia_results:
                results.extend(wikipedia_results)
            
            # Remove duplicates and limit results
            unique_results = []
            seen_titles = set()
            for result in results:
                if result['title'] not in seen_titles:
                    unique_results.append(result)
                    seen_titles.add(result['title'])
                    if len(unique_results) >= max_results:
                        break
            
            self.logger.info(f"Found {len(unique_results)} search results for: {query}")
            return unique_results
            
        except Exception as e:
            log_error(e, "web search", self.logger)
            return []
    
    def _search_duckduckgo(self, query: str) -> List[Dict]:
        """
        Search using DuckDuckGo instant answer API.
        
        Args:
            query (str): Search query
            
        Returns:
            List[Dict]: Search results
        """
        try:
            url = f"https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Abstract
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', query),
                    'snippet': data['Abstract'],
                    'url': data.get('AbstractURL', ''),
                    'source': 'DuckDuckGo'
                })
            
            # Related topics
            for topic in data.get('RelatedTopics', [])[:3]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'snippet': topic['Text'],
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo'
                    })
            
            return results
            
        except Exception as e:
            log_error(e, "DuckDuckGo search", self.logger)
            return []
    
    def _search_wikipedia(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search Wikipedia for information.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            List[Dict]: Wikipedia search results
        """
        try:
            # Search for pages
            search_results = wikipedia.search(query, results=max_results)
            results = []
            
            for title in search_results:
                try:
                    # Get page summary
                    summary = wikipedia.summary(title, sentences=2)
                    page = wikipedia.page(title)
                    
                    results.append({
                        'title': title,
                        'snippet': summary,
                        'url': page.url,
                        'source': 'Wikipedia'
                    })
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    # Try the first disambiguation option
                    try:
                        if e.options:
                            summary = wikipedia.summary(e.options[0], sentences=2)
                            page = wikipedia.page(e.options[0])
                            results.append({
                                'title': e.options[0],
                                'snippet': summary,
                                'url': page.url,
                                'source': 'Wikipedia'
                            })
                    except:
                        continue
                except wikipedia.exceptions.PageError:
                    continue
                except Exception as inner_e:
                    log_error(inner_e, f"Wikipedia page retrieval for {title}", self.logger)
                    continue
            
            return results
            
        except Exception as e:
            log_error(e, "Wikipedia search", self.logger)
            return []
    
    def get_weather(self, location: str = "current") -> Optional[Dict]:
        """
        Get weather information for a location.
        
        Args:
            location (str): Location name or "current" for current location
            
        Returns:
            Optional[Dict]: Weather information
        """
        try:
            if not WEATHER_API_KEY:
                # Fallback to web scraping
                return self._scrape_weather_fallback(location)
            
            # Use weather API (example with OpenWeatherMap)
            base_url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location if location != "current" else "auto:ip",
                'appid': WEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = self.session.get(base_url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            weather_info = {
                'location': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Retrieved weather for {location}")
            return weather_info
            
        except Exception as e:
            log_error(e, "weather retrieval", self.logger)
            return self._scrape_weather_fallback(location)
    
    def _scrape_weather_fallback(self, location: str) -> Optional[Dict]:
        """
        Fallback weather scraping method.
        
        Args:
            location (str): Location name
            
        Returns:
            Optional[Dict]: Basic weather information
        """
        try:
            # Use a simple weather service
            query = f"weather in {location}" if location != "current" else "current weather"
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract weather information from search results
            weather_div = soup.find('div', class_='weather-forecast')
            if weather_div:
                # Extract basic weather info
                temp = weather_div.find('span', class_='weather-forecast__temp')
                desc = weather_div.find('span', class_='weather-forecast__desc')
                
                return {
                    'location': location,
                    'temperature': temp.text if temp else 'Unknown',
                    'description': desc.text if desc else 'Unknown',
                    'source': 'Web scraping',
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            log_error(e, "weather fallback scraping", self.logger)
            return None
    
    def calculate_with_wolfram(self, query: str) -> Optional[str]:
        """
        Use Wolfram Alpha for calculations and queries.
        
        Args:
            query (str): Query to compute
            
        Returns:
            Optional[str]: Computation result
        """
        if not self.wolfram_client:
            return None
        
        try:
            res = self.wolfram_client.query(query)
            
            # Try to get the primary result
            if hasattr(res, 'results'):
                for result in res.results:
                    if hasattr(result, 'text'):
                        self.logger.info(f"Wolfram Alpha result for: {query}")
                        return result.text
            
            # Fallback to any pod with text
            for pod in res.pods:
                if hasattr(pod, 'text') and pod.text:
                    return pod.text
            
            return None
            
        except Exception as e:
            log_error(e, "Wolfram Alpha query", self.logger)
            return None
    
    def get_news_headlines(self, topic: str = "general", max_headlines: int = 5) -> List[Dict]:
        """
        Get news headlines for a topic.
        
        Args:
            topic (str): News topic
            max_headlines (int): Maximum number of headlines
            
        Returns:
            List[Dict]: News headlines
        """
        try:
            # Use a news aggregator or RSS feed
            # For demonstration, we'll scrape from a news site
            
            search_query = f"{topic} news"
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(search_query)}"
            
            response = self.session.get(search_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            headlines = []
            
            # Extract news links and titles
            news_links = soup.find_all('a', class_='result__a')[:max_headlines]
            
            for link in news_links:
                title = link.get_text(strip=True)
                url = link.get('href', '')
                
                if title and url:
                    headlines.append({
                        'title': title,
                        'url': url,
                        'source': 'News search',
                        'timestamp': datetime.now().isoformat()
                    })
            
            self.logger.info(f"Retrieved {len(headlines)} news headlines for: {topic}")
            return headlines
            
        except Exception as e:
            log_error(e, "news headline retrieval", self.logger)
            return []
    
    def scrape_page_content(self, url: str) -> Optional[Dict]:
        """
        Scrape content from a web page.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            Optional[Dict]: Page content
        """
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else 'No title'
            
            # Extract main content
            content_selectors = [
                'article', 'main', '.content', '#content',
                '.post-content', '.entry-content', 'section'
            ]
            
            content_text = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content_text = content_elem.get_text(strip=True)
                    break
            
            if not content_text:
                # Fallback to all paragraphs
                paragraphs = soup.find_all('p')
                content_text = ' '.join([p.get_text(strip=True) for p in paragraphs[:5]])
            
            return {
                'title': title_text,
                'content': content_text[:1000],  # Limit content length
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            log_error(e, f"page scraping for {url}", self.logger)
            return None
    
    def get_time_and_date(self, timezone: str = "local") -> Dict:
        """
        Get current time and date information.
        
        Args:
            timezone (str): Timezone (local or specific timezone)
            
        Returns:
            Dict: Time and date information
        """
        try:
            now = datetime.now()
            
            return {
                'current_time': now.strftime("%H:%M:%S"),
                'current_date': now.strftime("%Y-%m-%d"),
                'day_of_week': now.strftime("%A"),
                'month': now.strftime("%B"),
                'year': now.year,
                'formatted_datetime': now.strftime("%A, %B %d, %Y at %I:%M %p"),
                'timezone': timezone,
                'timestamp': now.isoformat()
            }
            
        except Exception as e:
            log_error(e, "time and date retrieval", self.logger)
            return {
                'error': 'Unable to retrieve time and date',
                'timestamp': datetime.now().isoformat()
            }