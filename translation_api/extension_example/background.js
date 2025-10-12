// Background script for the extension
chrome.runtime.onInstalled.addListener(() => {
    // Create context menu
    chrome.contextMenus.create({
        id: "translateText",
        title: "Translate '%s'",
        contexts: ["selection"]
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "translateText") {
        // Send message to content script to show translation popup
        chrome.tabs.sendMessage(tab.id, {
            action: "translate",
            text: info.selectionText
        });
    }
});