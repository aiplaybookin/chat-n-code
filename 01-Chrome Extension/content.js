const GEMINI_API_KEY = '<>';// Replace with your API key
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'scrapeProduct') {
    scrapeProductData().then(sendResponse);
    return true; // Required for async response
  }
});

async function scrapeProductData() {
  try {
    const pageContent = getVisiblePageContent();
    
    const prompt = `
    Analyze this product webpage content and extract the following information. 
    Return ONLY a JSON object with no additional formatting or markdown, using this exact structure:
    {
      "title": "exact product title",
      "price": "numerical price value only (no currency symbols)",
      "specs": ["key specification 1", "key specification 2", "etc"],
      "currency": "currency symbol or code"
    }

    Webpage content:
    ${pageContent}
    `;

    const productInfo = await callGeminiAPI(prompt);

    return {
      success: true,
      product: {
        ...productInfo,
        url: window.location.href,
        image: findProductImage(),
        vendor: new URL(window.location.href).hostname,
        scrapedAt: new Date().toISOString()
      }
    };
  } catch (error) {
    console.error('Scraping error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

async function callGeminiAPI(prompt) {
  try {
    const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: prompt
          }]
        }],
        generationConfig: {
          temperature: 0.2,
          topK: 40,
          topP: 0.8,
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.statusText}`);
    }

    const data = await response.json();
    const responseText = data.candidates[0].content.parts[0].text;
    
    // Clean up the response text by removing markdown formatting
    const cleanedResponse = cleanJsonResponse(responseText);
    
    try {
      return JSON.parse(cleanedResponse);
    } catch (parseError) {
      console.error('Parse error:', parseError);
      // Fallback to basic scraping if JSON parsing fails
      return fallbackScraping();
    }
  } catch (error) {
    console.error('Gemini API error:', error);
    // Fallback to basic scraping if API fails
    return fallbackScraping();
  }
}

function cleanJsonResponse(text) {
  // Remove markdown code blocks
  let cleaned = text.replace(/```json\n?/g, '').replace(/```\n?/g, '');
  
  // Remove any leading/trailing whitespace
  cleaned = cleaned.trim();
  
  // If the response starts with a newline or other characters before {, clean it
  const startBrace = cleaned.indexOf('{');
  const endBrace = cleaned.lastIndexOf('}');
  
  if (startBrace !== -1 && endBrace !== -1) {
    cleaned = cleaned.slice(startBrace, endBrace + 1);
  }
  
  return cleaned;
}

function fallbackScraping() {
  // Basic scraping as fallback
  const title = findElement([
    'h1',
    '[data-product-title]',
    '.product-title',
    '#product-title',
    '.product-name'
  ]);

  const price = findElement([
    '[data-price]',
    '.price',
    '.product-price',
    '.current-price',
    'span:contains($)',
    '.price-current'
  ]);

  const specs = Array.from(document.querySelectorAll('table tr, .specifications li'))
    .map(el => el.textContent.trim())
    .filter(text => text);

  return {
    title: title || 'Unknown Product',
    price: price ? price.replace(/[^\d.,]/g, '') : '',
    specs: specs,
    currency: price ? price.replace(/[\d.,\s]/g, '').trim() : '$'
  };
}

function getVisiblePageContent() {
  // Get main product content area
  const mainContent = findMainContentArea();
  
  // Extract text content
  let content = mainContent.innerText;
  
  // Clean up the content
  content = content
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 5000); // Limit content length for API

  return content;
}

function findMainContentArea() {
  // Try to find the main product content area using common selectors
  const selectors = [
    '[data-product-details]',
    '.product-details',
    '.product-main',
    'main',
    '#main-content',
    '.main-content'
  ];

  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      return element;
    }
  }

  // Fallback to body if no specific container is found
  return document.body;
}

function findProductImage() {
  const selectors = [
    '[data-main-image]',
    '.product-image img',
    '#main-product-image',
    '.gallery-image',
    'img[itemprop="image"]'
  ];

  for (const selector of selectors) {
    const img = document.querySelector(selector);
    if (img) {
      return img.src || img.getAttribute('data-src');
    }
  }

  // Fallback: find the largest image on the page
  const images = Array.from(document.images);
  let largestImage = null;
  let largestSize = 0;

  images.forEach(img => {
    const size = img.width * img.height;
    if (size > largestSize) {
      largestSize = size;
      largestImage = img;
    }
  });

  return largestImage ? largestImage.src : '';
}

// Add structured data extraction as fallback
function extractStructuredData() {
  const structuredData = {};
  const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
  
  jsonLdScripts.forEach(script => {
    try {
      const data = JSON.parse(script.textContent);
      if (data['@type'] === 'Product') {
        structuredData.title = data.name;
        structuredData.price = data.offers?.price;
        structuredData.currency = data.offers?.priceCurrency;
        structuredData.description = data.description;
      }
    } catch (e) {
      console.error('Error parsing structured data:', e);
    }
  });

  return structuredData;
}

// Helper function to clean text
function cleanText(text) {
  return text
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/[^\x20-\x7E]/g, ''); // Remove non-printable characters
} 