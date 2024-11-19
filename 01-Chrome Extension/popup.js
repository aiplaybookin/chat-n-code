document.getElementById('addProduct').addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Send message to content script to scrape the product
    chrome.tabs.sendMessage(tab.id, { action: 'scrapeProduct' }, async (response) => {
      if (response && response.success) {
        // Send the scraped product to background script
        chrome.runtime.sendMessage(
          { action: 'addProduct', product: response.product },
          (backgroundResponse) => {
            if (backgroundResponse.success) {
              alert('Product added successfully!');
            } else {
              alert('Error adding product: ' + backgroundResponse.message);
            }
          }
        );
      } else {
        alert('Error scraping product: ' + (response?.error || 'Unknown error'));
      }
    });
  } catch (error) {
    alert('Error: ' + error.message);
  }
});

document.getElementById('compareProducts').addEventListener('click', () => {
  window.open(chrome.runtime.getURL('compare.html'), '_blank');
}); 