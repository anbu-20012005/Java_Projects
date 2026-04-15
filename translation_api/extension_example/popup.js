// Popup script
document.addEventListener('DOMContentLoaded', () => {
    const testBtn = document.getElementById('testConnection');
    const statusDiv = document.getElementById('status');
    
    testBtn.addEventListener('click', async () => {
        testBtn.disabled = true;
        testBtn.textContent = 'Testing...';
        statusDiv.innerHTML = '';
        
        try {
            const response = await fetch('http://localhost:8000/health');
            
            if (response.ok) {
                const data = await response.json();
                statusDiv.innerHTML = `
                    <div class="status success">
                        ✅ API is running! Status: ${data.status}
                    </div>
                `;
            } else {
                throw new Error(`Server responded with status ${response.status}`);
            }
        } catch (error) {
            statusDiv.innerHTML = `
                <div class="status error">
                    ❌ Cannot connect to API server<br>
                    Make sure FastAPI is running on localhost:8000
                </div>
            `;
        } finally {
            testBtn.disabled = false;
            testBtn.textContent = 'Test API Connection';
        }
    });
});