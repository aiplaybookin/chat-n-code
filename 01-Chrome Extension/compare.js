document.addEventListener('DOMContentLoaded', () => {
  loadProducts();
  setupEventListeners();
});

function setupEventListeners() {
  // Search functionality
  document.querySelector('.search-box').addEventListener('input', (e) => {
    filterProducts(e.target.value);
  });

  // Sort buttons
  document.getElementById('sortPrice').addEventListener('click', () => {
    sortProducts('price');
  });

  document.getElementById('sortName').addEventListener('click', () => {
    sortProducts('name');
  });

  // Export button
  document.getElementById('exportData').addEventListener('click', exportToCSV);
}

function displayComparison(products) {
  const comparisonDiv = document.getElementById('comparison');

  if (!products || products.length === 0) {
    comparisonDiv.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-shopping-cart"></i>
        <h2>No products added yet</h2>
        <p>Start by adding products from different websites to compare them.</p>
      </div>
    `;
    return;
  }

  const table = `
    <table class="comparison-table">
      <thead>
        <tr>
          <th>Product</th>
          <th>Price</th>
          <th>Specifications</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        ${products.map(product => `
          <tr>
            <td>
              ${product.image ? `<img src="${product.image}" class="product-image" alt="${product.title}">` : ''}
              <a href="${product.url}" class="product-title" target="_blank">${product.title}</a>
              <div class="vendor">${product.vendor}</div>
            </td>
            <td class="price">${product.currency}${product.price}</td>
            <td>
              <ul class="specs-list">
                ${product.specs.map(spec => `<li>${spec}</li>`).join('')}
              </ul>
            </td>
            <td class="action-buttons">
              <button class="btn-icon btn-delete" onclick="removeProduct('${product.url}')">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  comparisonDiv.innerHTML = table;
}

function filterProducts(searchTerm) {
  chrome.storage.local.get(['products'], (data) => {
    const products = data.products || [];
    const filtered = products.filter(product => 
      product.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.specs.some(spec => spec.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    displayComparison(filtered);
  });
}

function sortProducts(by) {
  chrome.storage.local.get(['products'], (data) => {
    const products = [...(data.products || [])];
    
    if (by === 'price') {
      products.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
    } else if (by === 'name') {
      products.sort((a, b) => a.title.localeCompare(b.title));
    }

    displayComparison(products);
  });
}

function exportToCSV() {
  chrome.storage.local.get(['products'], (data) => {
    const products = data.products || [];
    const csvContent = [
      ['Title', 'Price', 'Currency', 'Specifications', 'URL', 'Vendor'],
      ...products.map(p => [
        p.title,
        p.price,
        p.currency,
        p.specs.join('; '),
        p.url,
        p.vendor
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'product-comparison.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
}

function removeProduct(url) {
  if (confirm('Are you sure you want to remove this product?')) {
    chrome.runtime.sendMessage(
      { action: 'removeProduct', url },
      response => {
        if (response.success) {
          loadProducts();
        } else {
          alert('Error removing product: ' + response.message);
        }
      }
    );
  }
}

function loadProducts() {
  chrome.runtime.sendMessage({ action: 'getProducts' }, response => {
    if (response.success) {
      displayComparison(response.products);
    } else {
      document.getElementById('comparison').innerHTML = 
        `<div class="empty-state">
          <i class="fas fa-exclamation-circle"></i>
          <h2>Error loading products</h2>
          <p>${response.message}</p>
        </div>`;
    }
  });
} 