// popup.js - Popup script for browser extension
document.addEventListener('DOMContentLoaded', function() {
    const API_URL = 'http://localhost:8000'; // Update this to your deployed FastAPI URL
    
    const quickText = document.getElementById('quickText');
    const fromLang = document.getElementById('fromLang');
    const toLang = document.getElementById('toLang');
    const translateBtn = document.getElementById('translateBtn');
    const result = document.getElementById('result');
    const resultText = document.getElementById('resultText');
    const copyBtn = document.getElementById('copyBtn');
    const status = document.getElementById('status');
    const error = document.getElementById('error');
    
    // Load saved preferences
    chrome.storage.sync.get(['defaultFromLang', 'defaultToLang'], function(data) {
        if (data.defaultFromLang) fromLang.value = data.defaultFromLang;
        if (data.defaultToLang) toLang.value = data.defaultToLang;
    });
    
    // Save preferences when changed
    fromLang.addEventListener('change', function() {
        chrome.storage.sync.set({defaultFromLang: fromLang.value});
    });
    
    toLang.addEventListener('change', function() {
        chrome.storage.sync.set({defaultToLang: toLang.value});
    });
    
    // Translate button click
    translateBtn.addEventListener('click', function() {
        const text = quickText.value.trim();
        
        if (!text) {
            showError('Please enter text to translate');
            return;
        }
        
        translateText(text, fromLang.value, toLang.value);
    });
    
    // Copy button click
    copyBtn.addEventListener('click', function() {
        navigator.clipboard.writeText(resultText.textContent).then(function() {
            copyBtn.textContent = 'Copied!';
            setTimeout(function() {
                copyBtn.textContent = 'Copy Result';
            }, 2000);
        }).catch(function(err) {
            console.error('Copy failed:', err);
            showError('Failed to copy text');
        });
    });
    
    // Enter key in textarea
    quickText.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            translateBtn.click();
        }
    });
    
    async function translateText(text, sourceLang, targetLang) {
        hideError();
        showStatus('Translating...');
        translateBtn.disabled = true;
        result.style.display = 'none';
        
        try {
            const response = await fetch(`${API_URL}/translate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    source_language: sourceLang,
                    target_language: targetLang
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Show result
            resultText.textContent = data.translated_text;
            result.style.display = 'block';
            showStatus(`Translated from ${sourceLang} to ${targetLang}`);
            
        } catch (err) {
            console.error('Translation error:', err);
            showError(`Translation failed: ${err.message}`);
        } finally {
            translateBtn.disabled = false;
        }
    }
    
    function showStatus(message) {
        status.textContent = message;
        status.style.color = '#666';
    }
    
    function showError(message) {
        error.textContent = message;
        error.style.display = 'block';
        status.textContent = '';
    }
    
    function hideError() {
        error.style.display = 'none';
    }
    
    // Check API status on popup open
    checkApiStatus();
    
    async function checkApiStatus() {
        try {
            const response = await fetch(`${API_URL}/health`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                showStatus('API service is running');
            } else {
                showError('API service is not responding properly');
            }
        } catch (err) {
            showError('Cannot connect to translation service. Make sure the FastAPI server is running.');
        }
    }
});