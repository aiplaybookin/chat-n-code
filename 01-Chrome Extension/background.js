// Listen for installation
chrome.runtime.onInstalled.addListener(() => {
  // Initialize storage with empty products array and default settings
  chrome.storage.local.set({
    products: [],
    settings: {
      geminiApiKey: '' // Store API key securely
    }
  });
});

// Listen for messages from content script and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'addProduct':
      handleAddProduct(request.product, sendResponse);
      break;
    case 'getProducts':
      handleGetProducts(sendResponse);
      break;
    case 'removeProduct':
      handleRemoveProduct(request.url, sendResponse);
      break;
  }
  // Return true to indicate we'll send a response asynchronously
  return true;
});

async function handleAddProduct(product, sendResponse) {
  try {
    const data = await chrome.storage.local.get(['products']);
    const products = data.products || [];
    
    // Check if product already exists
    const existingIndex = products.findIndex(p => p.url === product.url);
    
    if (existingIndex !== -1) {
      // Update existing product
      products[existingIndex] = {
        ...product,
        updatedAt: new Date().toISOString()
      };
    } else {
      // Add new product
      products.push({
        ...product,
        addedAt: new Date().toISOString()
      });
    }

    await chrome.storage.local.set({ products });
    sendResponse({ success: true, message: 'Product added successfully' });
  } catch (error) {
    sendResponse({ success: false, message: error.message });
  }
}

async function handleGetProducts(sendResponse) {
  try {
    const data = await chrome.storage.local.get(['products']);
    sendResponse({ success: true, products: data.products || [] });
  } catch (error) {
    sendResponse({ success: false, message: error.message });
  }
}

async function handleRemoveProduct(url, sendResponse) {
  try {
    const data = await chrome.storage.local.get(['products']);
    const products = data.products || [];
    
    const filteredProducts = products.filter(p => p.url !== url);
    await chrome.storage.local.set({ products: filteredProducts });
    
    sendResponse({ success: true, message: 'Product removed successfully' });
  } catch (error) {
    sendResponse({ success: false, message: error.message });
  }
}

// Add a function to handle API key updates
async function updateApiKey(apiKey) {
  await chrome.storage.local.set({
    settings: {
      geminiApiKey: apiKey
    }
  });
} 