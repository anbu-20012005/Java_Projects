// content.js - Content script for browser extension
// This script runs on web pages and handles text selection and translation

class TranslationExtension {
    constructor() {
        this.apiUrl = 'http://localhost:8000'; // Update this to your deployed FastAPI URL
        this.selectedText = '';
        this.translationPopup = null;
        this.init();
    }

    init() {
        // Listen for text selection
        document.addEventListener('mouseup', this.handleTextSelection.bind(this));
        
        // Listen for keydown events (e.g., Ctrl+T for translate)
        document.addEventListener('keydown', this.handleKeydown.bind(this));
        
        // Close popup when clicking outside
        document.addEventListener('click', this.handleDocumentClick.bind(this));
    }

    handleTextSelection(event) {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();
        
        if (selectedText.length > 0) {
            this.selectedText = selectedText;
            this.showTranslationButton(event);
        } else {
            this.hideTranslationButton();
        }
    }

    handleKeydown(event) {
        // Translate selected text with Ctrl+T
        if (event.ctrlKey && event.key === 't' && this.selectedText) {
            event.preventDefault();
            this.translateSelectedText();
        }
    }

    handleDocumentClick(event) {
        if (this.translationPopup && !this.translationPopup.contains(event.target)) {
            this.hideTranslationButton();
        }
    }

    showTranslationButton(event) {
        this.hideTranslationButton(); // Remove existing popup
        
        const popup = document.createElement('div');
        popup.className = 'translation-popup';
        popup.innerHTML = `
            <div class="translation-header">
                <span>Translate: "${this.selectedText.substring(0, 50)}${this.selectedText.length > 50 ? '...' : ''}"</span>
                <button class="close-btn">×</button>
            </div>
            <div class="language-selectors">
                <select class="source-lang">
                    <option value="English">English</option>
                    <option value="Tamil">Tamil</option>
                    <option value="Hindi">Hindi</option>
                    <option value="French">French</option>
                    <option value="Spanish">Spanish</option>
                    <option value="German">German</option>
                    <option value="Chinese">Chinese</option>
                    <option value="Japanese">Japanese</option>
                    <option value="Korean">Korean</option>
                    <option value="Malayalam">Malayalam</option>
                </select>
                <span>→</span>
                <select class="target-lang">
                    <option value="Tamil">Tamil</option>
                    <option value="English">English</option>
                    <option value="Hindi">Hindi</option>
                    <option value="French">French</option>
                    <option value="Spanish">Spanish</option>
                    <option value="German">German</option>
                    <option value="Chinese">Chinese</option>
                    <option value="Japanese">Japanese</option>
                    <option value="Korean">Korean</option>
                    <option value="Malayalam">Malayalam</option>
                </select>
            </div>
            <button class="translate-btn">Translate</button>
            <div class="translation-result" style="display: none;">
                <div class="result-text"></div>
                <button class="copy-btn">Copy</button>
            </div>
            <div class="loading" style="display: none;">Translating...</div>
        `;

        // Style the popup
        popup.style.cssText = `
            position: absolute;
            top: ${event.pageY + 10}px;
            left: ${event.pageX}px;
            background: white;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-family: Arial, sans-serif;
            font-size: 14px;
            min-width: 300px;
            max-width: 400px;
        `;

        document.body.appendChild(popup);
        this.translationPopup = popup;

        // Add event listeners
        popup.querySelector('.close-btn').addEventListener('click', () => {
            this.hideTranslationButton();
        });

        popup.querySelector('.translate-btn').addEventListener('click', () => {
            this.translateSelectedText();
        });

        popup.querySelector('.copy-btn').addEventListener('click', () => {
            this.copyToClipboard();
        });
    }

    hideTranslationButton() {
        if (this.translationPopup) {
            this.translationPopup.remove();
            this.translationPopup = null;
        }
    }

    async translateSelectedText() {
        if (!this.translationPopup) return;

        const sourceLang = this.translationPopup.querySelector('.source-lang').value;
        const targetLang = this.translationPopup.querySelector('.target-lang').value;
        const loadingDiv = this.translationPopup.querySelector('.loading');
        const resultDiv = this.translationPopup.querySelector('.translation-result');
        const resultText = this.translationPopup.querySelector('.result-text');

        // Show loading
        loadingDiv.style.display = 'block';
        resultDiv.style.display = 'none';

        try {
            const response = await fetch(`${this.apiUrl}/translate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: this.selectedText,
                    source_language: sourceLang,
                    target_language: targetLang
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Show result
            resultText.textContent = result.translated_text;
            loadingDiv.style.display = 'none';
            resultDiv.style.display = 'block';

        } catch (error) {
            console.error('Translation error:', error);
            resultText.textContent = `Error: ${error.message}`;
            loadingDiv.style.display = 'none';
            resultDiv.style.display = 'block';
        }
    }

    async copyToClipboard() {
        const resultText = this.translationPopup.querySelector('.result-text').textContent;
        try {
            await navigator.clipboard.writeText(resultText);
            
            // Show copied feedback
            const copyBtn = this.translationPopup.querySelector('.copy-btn');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        } catch (error) {
            console.error('Copy failed:', error);
        }
    }
}

// Initialize the extension when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new TranslationExtension();
    });
} else {
    new TranslationExtension();
}