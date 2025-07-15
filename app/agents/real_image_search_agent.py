from typing import Dict, Any, List
import logging
import os
from datetime import datetime
import re
import json
import aiohttp
import aiofiles
import hashlib
from PIL import Image
import io

from .base_agent import BaseAgent
from ..models import AgentResponse

logger = logging.getLogger(__name__)

class RealImageSearchAgent(BaseAgent):
    """
    Agent that searches for real images on Google and downloads them locally.
    """
    
    def __init__(self):
        super().__init__("RealImageSearchAgent", temperature=0.3)
        self.images_dir = "downloaded_images"
        self.max_images = 8
        self.session = None
        
        # Create images directory if it doesn't exist
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Google Images search headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    def get_system_prompt(self) -> str:
        return """You are an expert in product analysis and image search for Amazon listings.

Your job is to:
1. Analyze product context (name, category, features, description)
2. Identify the specific product type
3. Generate specific and relevant search terms
4. Provide image search recommendations to maximize sales

Be very specific in your analysis. For example:
- "Audífonos Profesionales Gaming RGB" -> terms: "gaming headset", "rgb gaming headphones", "professional gaming audio"
- "Mate de vidrio Premium" -> terms: "glass mate cup", "traditional mate", "premium glass cup"
- "Mochila Escolar Resistente" -> terms: "school backpack", "durable student bag", "educational backpack"

Provide precise and contextual responses in JSON format."""

    async def _analyze_product_with_llm(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to analyze product context and generate specific search terms.
        """
        product_name = product_data.get("product_name", "")
        category = product_data.get("category", "")
        features = product_data.get("features", [])
        description = product_data.get("description", "")
        
        # Create prompt for contextual analysis
        prompt = f"""
Analyze this product and generate specific search terms for finding relevant images:

PRODUCT: {product_name}
CATEGORY: {category}
FEATURES: {', '.join(features) if features else 'Not specified'}
DESCRIPTION: {description}

Provide your analysis in JSON format:
{{
    "product_type": "specific product type",
    "primary_search_terms": ["term1", "term2", "term3"],
    "secondary_search_terms": ["term4", "term5"],
    "image_contexts": ["context1", "context2", "context3"],
    "confidence": 0.95,
    "recommendations": ["recommendation1", "recommendation2", "recommendation3"]
}}

Examples:
- "Audífonos Gaming RGB" -> "gaming_headset", terms: ["gaming headset", "rgb gaming headphones", "professional gaming audio"]
- "Mate de vidrio Premium" -> "mate_cup", terms: ["glass mate cup", "traditional mate", "premium glass cup"]
- "Smartwatch Deportivo" -> "fitness_smartwatch", terms: ["fitness smartwatch", "sport watch", "health tracker"]

Be very specific and precise.
"""
        
        try:
            response = await self.ollama_service.generate_response(prompt)
            
            if response.get("success"):
                content = response.get("content", "")
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    return analysis
                else:
                    logger.warning("Could not extract JSON from LLM analysis")
                    return self._fallback_analysis(product_data)
            else:
                logger.warning(f"LLM error: {response.get('error')}")
                return self._fallback_analysis(product_data)
                
        except Exception as e:
            logger.error(f"Error in contextual analysis: {e}")
            return self._fallback_analysis(product_data)
    
    def _fallback_analysis(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback analysis based on specific rules for different products.
        """
        product_name = product_data.get("product_name", "").lower()
        category = product_data.get("category", "").lower()
        features = [str(f).lower() for f in product_data.get("features", [])]
        description = product_data.get("description", "").lower()
        
        # Gaming headphones detection - enhanced with features and description
        if (any(term in product_name for term in ["audifonos", "headphones", "headset", "auriculares"]) or 
            any(term in description for term in ["headset", "headphones", "audio"]) or
            "electronics" in category):
            
            # Check for gaming context
            gaming_indicators = ["gaming", "rgb", "profesional", "gamer", "esports", "pc"]
            if (any(term in product_name for term in gaming_indicators) or 
                any(term in description for term in gaming_indicators) or
                any(term in " ".join(features) for term in gaming_indicators)):
                
                return {
                    "product_type": "gaming_headset",
                    "primary_search_terms": ["gaming headset", "rgb gaming headphones", "professional gaming audio"],
                    "secondary_search_terms": ["esports headset", "gaming setup", "pc gaming audio"],
                    "image_contexts": ["gaming setup", "professional studio", "esports context"],
                    "confidence": 0.9,
                    "recommendations": [
                        "Search for specific gaming headset images with RGB",
                        "Include professional gaming setup context",
                        "Show technical features like drivers and connectivity"
                    ]
                }
            else:
                return {
                    "product_type": "headphones",
                    "primary_search_terms": ["professional headphones", "audio headphones", "studio headphones"],
                    "secondary_search_terms": ["music headphones", "audio equipment", "sound quality"],
                    "image_contexts": ["professional audio", "studio setup", "music context"],
                    "confidence": 0.85,
                    "recommendations": [
                        "Search for professional headphone images",
                        "Include music studio context",
                        "Show audio quality and premium materials"
                    ]
                }
        
        # Mate detection
        elif any(term in product_name for term in ["mate", "glass", "vidrio"]):
            return {
                "product_type": "mate_cup",
                "primary_search_terms": ["glass mate cup", "traditional mate", "argentine mate"],
                "secondary_search_terms": ["tea cup", "traditional drink", "glass cup"],
                "image_contexts": ["traditional setting", "kitchen context", "cultural context"],
                "confidence": 0.9,
                "recommendations": [
                    "Search for traditional and cultural mate images",
                    "Include traditional usage context",
                    "Show glass quality and design"
                ]
            }
        
        # Smartwatch detection
        elif any(term in product_name for term in ["smartwatch", "watch", "reloj"]):
            return {
                "product_type": "smartwatch",
                "primary_search_terms": ["apple watch", "smartwatch", "fitness tracker"],
                "secondary_search_terms": ["wearable tech", "smart device", "fitness watch"],
                "image_contexts": ["lifestyle", "fitness context", "tech showcase"],
                "confidence": 0.85,
                "recommendations": [
                    "Search for smartwatch in use images",
                    "Include fitness and lifestyle context",
                    "Show technical features and apps"
                ]
            }
        
        # Backpack detection
        elif any(term in product_name for term in ["mochila", "backpack", "bag"]):
            return {
                "product_type": "backpack",
                "primary_search_terms": ["school backpack", "student backpack", "travel backpack"],
                "secondary_search_terms": ["laptop bag", "hiking backpack", "educational bag"],
                "image_contexts": ["school context", "travel context", "outdoor lifestyle"],
                "confidence": 0.85,
                "recommendations": [
                    "Search for backpack in school context",
                    "Include travel and outdoor context",
                    "Show capacity and internal organization"
                ]
            }
        
        # Generic fallback
        else:
            return {
                "product_type": "generic_product",
                "primary_search_terms": [product_name.replace(" ", "+")],
                "secondary_search_terms": [category],
                "image_contexts": ["product showcase", "studio shot"],
                "confidence": 0.6,
                "recommendations": ["Search for specific product images"]
            }
    
    async def _search_google_images(self, query: str, num_images: int = 5) -> List[str]:
        """
        Search for images using Google Images search.
        """
        try:
            logger.info(f"Searching Google Images for '{query}' with {num_images} images")
            
            # Try Google Images search first
            urls = await self._try_google_search(query, num_images)
            
            if urls:
                logger.info(f"Found {len(urls)} images from Google Images for '{query}'")
                return urls
            
            # If no images found, try alternative search
            logger.warning(f"No images found in Google Images for '{query}', trying alternative search")
            return await self._search_alternative_sources(query, num_images)
                    
        except Exception as e:
            logger.error(f"Error in Google Images search for '{query}': {e}")
            return await self._search_alternative_sources(query, num_images)
    
    async def _try_google_search(self, query: str, num_images: int) -> List[str]:
        """
        Try to search Google Images for real images.
        """
        try:
            session = await self._get_session()
            
            # Google Images search URL - improved with better parameters
            search_url = f"https://www.google.com/search?tbm=isch&q={query.replace(' ', '+')}&safe=off&tbs=isz:m"
            
            logger.info(f"Searching Google Images: {search_url}")
            
            # Add additional headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            async with session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    logger.info(f"Google Images search successful for '{query}' - response length: {len(html)}")
                    urls = self._extract_image_urls(html, num_images)
                    logger.info(f"Extracted {len(urls)} URLs from Google Images for '{query}'")
                    return urls
                else:
                    logger.warning(f"Google Images search failed with status {response.status} for '{query}'")
                    return []
                    
        except Exception as e:
            logger.error(f"Error in Google Images search for '{query}': {e}")
            return []
    
    def _extract_image_urls(self, html: str, num_images: int) -> List[str]:
        """
        Extract image URLs from Google Images HTML - improved and simplified.
        """
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html, 'html.parser')
            urls = []
            
            # Try different extraction methods
            urls.extend(self._extract_urls_from_scripts(soup, num_images - len(urls)))
            
            if len(urls) < num_images:
                urls.extend(self._extract_urls_from_img_tags(soup, num_images - len(urls)))
            
            if len(urls) < num_images:
                urls.extend(self._extract_urls_from_data_attributes(soup, num_images - len(urls)))
            
            # Remove duplicates while preserving order
            unique_urls = []
            for url in urls:
                if url not in unique_urls:
                    unique_urls.append(url)
            
            logger.info(f"Successfully extracted {len(unique_urls)} image URLs from Google Images HTML")
            return unique_urls[:num_images]
            
        except Exception as e:
            logger.error(f"Error extracting image URLs from HTML: {e}")
            return []
    
    def _extract_urls_from_scripts(self, soup, max_urls: int) -> List[str]:
        """Extract image URLs from script tags."""
        import re
        
        urls = []
        scripts = soup.find_all('script')
        url_pattern = r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s"\'<>]*)?'
        
        for script in scripts:
            if not script.string or 'https' not in script.string:
                continue
                
            found_urls = re.findall(url_pattern, script.string, re.IGNORECASE)
            
            for url in found_urls:
                if self._is_valid_image_url(url):
                    urls.append(url)
                    if len(urls) >= max_urls:
                        return urls
        
        return urls
    
    def _extract_urls_from_img_tags(self, soup, max_urls: int) -> List[str]:
        """Extract image URLs from img tags."""
        urls = []
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src', '')
            if self._is_valid_image_url(src):
                urls.append(src)
                if len(urls) >= max_urls:
                    break
        
        return urls
    
    def _extract_urls_from_data_attributes(self, soup, max_urls: int) -> List[str]:
        """Extract image URLs from data attributes."""
        urls = []
        elements_with_data = soup.find_all(attrs={'data-src': True})
        
        for element in elements_with_data:
            data_src = element.get('data-src', '')
            if self._is_valid_image_url(data_src):
                urls.append(data_src)
                if len(urls) >= max_urls:
                    break
        
        return urls
    
    def _process_pattern_matches(self, matches: List, max_urls: int) -> List[str]:
        """Process regex matches to extract valid URLs."""
        return []
    
    def _is_valid_image_url(self, url: str) -> bool:
        """
        Check if URL is a valid image URL.
        """
        if not url or not url.startswith('http'):
            return False
            
        # Check if it's a valid image extension
        if not any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
            return False
            
        # Filter out Google's internal URLs and thumbnails
        invalid_patterns = [
            'google.com/images/branding/',
            'gstatic.com',
            'encrypted-tbn',
            'data:image',
            'googleusercontent.com',
            '/search?',
            'base64'
        ]
        
        for pattern in invalid_patterns:
            if pattern in url.lower():
                return False
                
        # Check minimum URL length
        if len(url) < 20:
            return False
            
        return True
    
    async def _search_alternative_sources(self, query: str, num_images: int) -> List[str]:
        """
        Search alternative sources when Google Images fails.
        """
        try:
            logger.info(f"Searching alternative sources for '{query}'")
            
            # Try Unsplash as alternative - search dynamically, no hardcoded URLs
            return await self._search_unsplash_images(query, num_images)
            
        except Exception as e:
            logger.error(f"Error in alternative search for '{query}': {e}")
            # Return empty list instead of placeholder - no hardcoded images
            logger.warning(f"No images found for '{query}' - returning empty list")
            return []
    async def _search_unsplash_images(self, query: str, num_images: int = 5) -> List[str]:
        """
        Search Unsplash for images as fallback - dynamic search only.
        """
        try:
            session = await self._get_session()
            
            # Unsplash search URL
            search_url = f"https://unsplash.com/s/photos/{query.replace(' ', '-')}"
            
            async with session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._extract_unsplash_urls(html, num_images)
                else:
                    logger.warning(f"Unsplash search failed with status {response.status}")
                    return []
            
        except Exception as e:
            logger.error(f"Error in Unsplash search for '{query}': {e}")
            return []
    
    def _extract_unsplash_urls(self, html: str, num_images: int) -> List[str]:
        """
        Extract image URLs from Unsplash HTML.
        """
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html, 'html.parser')
            urls = []
            
            # Look for Unsplash image URLs
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src', '')
                if 'images.unsplash.com' in src and 'photo-' in src:
                    # Convert to a standard size
                    clean_url = src.split('?')[0] + '?w=800&h=600&fit=crop'
                    urls.append(clean_url)
                    if len(urls) >= num_images:
                        break
            
            logger.info(f"Extracted {len(urls)} Unsplash image URLs")
            return urls[:num_images]
            
        except Exception as e:
            logger.error(f"Error extracting Unsplash URLs: {e}")
            return []
    
    async def _download_image(self, url: str, filename: str) -> Dict[str, Any]:
        """
        Download an image from URL and save it locally.
        """
        try:
            session = await self._get_session()
            
            logger.info(f"Attempting to download image from: {url}")
            
            async with session.get(url) as response:
                logger.info(f"Response status: {response.status}")
                
                if response.status == 200:
                    content = await response.read()
                    logger.info(f"Downloaded {len(content)} bytes from {url}")
                    
                    # Verify it's a valid image
                    try:
                        img = Image.open(io.BytesIO(content))
                        img.verify()
                        logger.info(f"Image validation successful for {url}")
                    except Exception as e:
                        logger.warning(f"Invalid image from {url}: {e}")
                        return {}
                    
                    # Save the image
                    filepath = os.path.join(self.images_dir, filename)
                    
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content)
                    
                    logger.info(f"Image saved successfully to {filepath}")
                    
                    # Create thumbnail
                    thumbnail_filename = f"thumb_{filename}"
                    thumbnail_path = os.path.join(self.images_dir, thumbnail_filename)
                    
                    try:
                        img = Image.open(io.BytesIO(content))
                        img.thumbnail((200, 150))
                        img.save(thumbnail_path)
                        logger.info(f"Thumbnail created at {thumbnail_path}")
                    except Exception as e:
                        logger.warning(f"Could not create thumbnail: {e}")
                        thumbnail_filename = filename
                        thumbnail_path = filepath
                    
                    return {
                        "local_path": filepath,
                        "filename": filename,
                        "thumbnail_path": thumbnail_path,
                        "thumbnail_filename": thumbnail_filename,
                        "original_url": url,
                        "size": len(content),
                        "status": "downloaded"
                    }
                else:
                    logger.warning(f"Failed to download image from {url}: status {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return {}
    
    async def _process_search_term(self, term: str, max_images: int = 2) -> List[Dict[str, Any]]:
        """
        Process a search term: search for images and download them.
        """
        downloaded_images = []
        
        logger.info(f"Processing search term: '{term}' (max_images: {max_images})")
        
        # Search for images
        image_urls = await self._search_google_images(term, max_images)
        
        if not image_urls:
            logger.warning(f"No images found for term: {term}")
            return []
        
        logger.info(f"Found {len(image_urls)} URLs for term '{term}': {image_urls}")
        
        # Download images
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, url in enumerate(image_urls):
            try:
                # Generate a unique filename
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"{term.replace(' ', '_')}_{timestamp}_{i+1}_{url_hash}.jpg"
                
                logger.info(f"Downloading image {i+1}/{len(image_urls)} for term '{term}': {url}")
                
                # Download the image
                image_data = await self._download_image(url, filename)
                
                if image_data:
                    image_data.update({
                        "search_term": term,
                        "relevance_score": 0.9 - (i * 0.1),  # Higher score for first results
                        "description": f"Image for {term}"
                    })
                    downloaded_images.append(image_data)
                    logger.info(f"Successfully downloaded image {i+1} for term '{term}': {filename}")
                else:
                    logger.warning(f"Failed to download image {i+1} for term '{term}' from {url}")
                    
            except Exception as e:
                logger.error(f"Error processing image {i+1} for term '{term}': {e}")
                continue
        
        logger.info(f"Downloaded {len(downloaded_images)} images for term '{term}'")
        return downloaded_images
    
    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """
        Process image search using contextual analysis and real image downloads.
        """
        start_time = datetime.now()
        
        try:
            product_data = data.get("product_data", {})
            
            # 1. Contextual analysis of the product using LLM
            analysis = await self._analyze_product_with_llm(product_data)
            
            # 2. Search and download real images
            downloaded_images = []
            
            # Process primary search terms
            primary_terms = analysis.get("primary_search_terms", [])
            for term in primary_terms[:3]:  # Limit to 3 primary terms
                images = await self._process_search_term(term, 2)  # 2 images per term
                downloaded_images.extend(images)
            
            # Process secondary search terms if we need more images
            if len(downloaded_images) < self.max_images:
                secondary_terms = analysis.get("secondary_search_terms", [])
                remaining_slots = self.max_images - len(downloaded_images)
                
                for term in secondary_terms[:remaining_slots]:
                    images = await self._process_search_term(term, 1)  # 1 image per secondary term
                    downloaded_images.extend(images)
            
            # 3. Organize images by categories
            image_categories = {}
            
            for img in downloaded_images:
                term = img.get("search_term", "general")
                if term not in image_categories:
                    image_categories[term] = []
                image_categories[term].append(img)
            
            # 4. Generate recommendations
            recommendations = analysis.get("recommendations", [])
            recommendations.extend([
                f"Downloaded {len(downloaded_images)} real images for {analysis['product_type']}",
                f"Contextual analysis completed with {analysis.get('confidence', 0.8)*100:.0f}% confidence",
                "Images optimized for Amazon conversion and locally accessible"
            ])
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AgentResponse(
                agent_name=self.agent_name,
                status="success",
                confidence=analysis.get("confidence", 0.8),
                processing_time=processing_time,
                data={
                    "product_type_detected": analysis["product_type"],
                    "downloaded_images": downloaded_images,
                    "image_categories": image_categories,
                    "search_terms_used": analysis.get("primary_search_terms", []) + analysis.get("secondary_search_terms", []),
                    "analysis_result": analysis,
                    "total_images_downloaded": len(downloaded_images),
                    "images_by_term": {term: len(images) for term, images in image_categories.items()}
                },
                recommendations=recommendations,
                notes=[f"Real image search completed for {analysis['product_type']} with {len(downloaded_images)} images downloaded"]
            )
            
        except Exception as e:
            logger.error(f"Error in RealImageSearchAgent: {e}")
            return AgentResponse(
                agent_name=self.agent_name,
                status="error",
                confidence=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                data={"error": str(e)},
                recommendations=["Error in real image search, check configuration"],
                notes=[f"Error: {str(e)}"]
            )
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
