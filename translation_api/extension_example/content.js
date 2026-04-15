// Content script - handles text selection and translation
class TextTranslator {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.selectedText = '';
        this.init();
    }

    init() {
        // Add context menu listener
        document.addEventListener('mouseup', (e) => {
            const selection = window.getSelection();
            if (selection.toString().trim().length > 0) {
                this.selectedText = selection.toString().trim();
                this.showTranslationPopup(e.pageX, e.pageY);
            }
        });

        // Hide popup when clicking elsewhere
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.translator-popup')) {
                this.hideTranslationPopup();
            }
        });
    }

    showTranslationPopup(x, y) {
        // Remove existing popup
        this.hideTranslationPopup();

        // Create popup element
        const popup = document.createElement('div');
        popup.className = 'translator-popup';
        popup.innerHTML = `
            <div class="translator-content">
                <div class="translator-header">
                    <span>Translate: "${this.selectedText.substring(0, 30)}${this.selectedText.length > 30 ? '...' : ''}"</span>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="translator-controls">
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
                        <option value="Spanish">Spanish</option>
                        <option value="English">English</option>
                        <option value="Tamil">Tamil</option>
                        <option value="Hindi">Hindi</option>
                        <option value="French">French</option>
                        <option value="German">German</option>
                        <option value="Chinese">Chinese</option>
                        <option value="Japanese">Japanese</option>
                        <option value="Korean">Korean</option>
                        <option value="Malayalam">Malayalam</option>
                    </select>
                    <button class="translate-btn">Translate</button>
                </div>
                <div class="translation-result"></div>
            </div>
        `;

        // Position popup
        popup.style.position = 'absolute';
        popup.style.left = x + 'px';
        popup.style.top = y + 'px';
        popup.style.zIndex = '10000';

        // Add styles
        this.addPopupStyles();

        document.body.appendChild(popup);

        // Add event listeners
        popup.querySelector('.close-btn').addEventListener('click', () => {
            this.hideTranslationPopup();
        });

        popup.querySelector('.translate-btn').addEventListener('click', () => {
            this.translateSelectedText(popup);
        });
    }

    hideTranslationPopup() {
        const existingPopup = document.querySelector('.translator-popup');
        if (existingPopup) {
            existingPopup.remove();
        }
    }

    async translateSelectedText(popup) {
        const sourceLang = popup.querySelector('.source-lang').value;
        const targetLang = popup.querySelector('.target-lang').value;
        const resultDiv = popup.querySelector('.translation-result');
        const translateBtn = popup.querySelector('.translate-btn');

        // Show loading state
        translateBtn.disabled = true;
        translateBtn.textContent = 'Translating...';
        resultDiv.innerHTML = '<div class="loading">Translating...</div>';

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
            resultDiv.innerHTML = `
                <div class="translation-text">
                    <strong>Translation:</strong><br>
                    ${result.translated_text}
                </div>
            `;

        } catch (error) {
            console.error('Translation error:', error);
            resultDiv.innerHTML = `
                <div class="error">
                    Translation failed: ${error.message}
                    <br><small>Make sure the FastAPI server is running on localhost:8000</small>
                </div>
            `;
        } finally {
            translateBtn.disabled = false;
            translateBtn.textContent = 'Translate';
        }
    }

    addPopupStyles() {
        if (document.getElementById('translator-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'translator-styles';
        styles.textContent = `
            .translator-popup {
                background: white;
                border: 2px solid #007bff;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                min-width: 350px;
                max-width: 500px;
            }

            .translator-content {
                padding: 16px;
            }

            .translator-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
                font-weight: 600;
                color: #333;
            }

            .close-btn {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                color: #666;
                padding: 0;
                width: 20px;
                height: 20px;
            }

            .close-btn:hover {
                color: #000;
            }

            .translator-controls {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 12px;
                flex-wrap: wrap;
            }

            .translator-controls select {
                padding: 6px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }

            .translate-btn {
                background: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }

            .translate-btn:hover:not(:disabled) {
                background: #0056b3;
            }

            .translate-btn:disabled {
                background: #6c757d;
                cursor: not-allowed;
            }

            .translation-result {
                min-height: 20px;
            }

            .translation-text {
                background: #f8f9fa;
                padding: 12px;
                border-radius: 4px;
                border-left: 4px solid #28a745;
            }

            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 12px;
                border-radius: 4px;
                border-left: 4px solid #dc3545;
            }

            .loading {
                text-align: center;
                color: #666;
                font-style: italic;
            }
        `;
        document.head.appendChild(styles);
    }
}

// Initialize the translator when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new TextTranslator();
    });
} else {
    new TextTranslator();
}