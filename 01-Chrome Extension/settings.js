document.addEventListener('DOMContentLoaded', async () => {
  // Load existing settings
  const data = await chrome.storage.local.get(['settings']);
  if (data.settings?.geminiApiKey) {
    document.getElementById('apiKey').value = data.settings.geminiApiKey;
  }
});

document.getElementById('saveSettings').addEventListener('click', async () => {
  const apiKey = document.getElementById('apiKey').value.trim();
  
  await chrome.storage.local.set({
    settings: {
      geminiApiKey: apiKey
    }
  });
  
  alert('Settings saved successfully!');
}); 