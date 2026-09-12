```javascript
// ============================================================
// WALAWWA WEB DOWNLOAD
// ============================================================
// Flow:
//
// Telegram post
//      ↓
// https://walwwa.web.app/?start=CODE
//      ↓
// Website
//      ↓
// User presses Download
//      ↓
// https://t.me/walawwa_downloadBot?start=CODE
//      ↓
// Telegram bot receives CODE
//      ↓
// Bot gets file information from Firebase
//      ↓
// Bot sends the stored Telegram file to the user
//
// The WEBSITE DOES NOT download or store the file.
// ============================================================


const TELEGRAM_BOT = "walawwa_downloadBot";


// ============================================================
// PAGE ELEMENTS
// ============================================================

let downloadButton = null;
let errorBox = null;
let statusBox = null;


// ============================================================
// GET DOWNLOAD CODE
// ============================================================

function getDownloadCode() {
    const params = new URLSearchParams(window.location.search);

    // Main format:
    // ?start=XXXXXXXX

    const startCode = params.get("start");

    if (startCode) {
        return startCode.trim();
    }

    // Also support:
    // ?code=XXXXXXXX

    const code = params.get("code");

    if (code) {
        return code.trim();
    }

    return "";
}


// ============================================================
// SHOW ERROR
// ============================================================

function showError(message) {
    if (errorBox) {
        errorBox.textContent = message;
        errorBox.style.display = "block";
    }
}


// ============================================================
// HIDE ERROR
// ============================================================

function hideError() {
    if (errorBox) {
        errorBox.textContent = "";
        errorBox.style.display = "none";
    }
}


// ============================================================
// SHOW STATUS
// ============================================================

function showStatus(message) {
    if (statusBox) {
        statusBox.textContent = message;
        statusBox.style.display = "block";
    }
}


// ============================================================
// HIDE STATUS
// ============================================================

function hideStatus() {
    if (statusBox) {
        statusBox.textContent = "";
        statusBox.style.display = "none";
    }
}


// ============================================================
// GET DOWNLOAD BUTTON
// ============================================================

function findDownloadButton() {

    // Try common IDs first.

    let button = document.getElementById("download-btn");

    if (button) {
        return button;
    }

    button = document.getElementById("downloadButton");

    if (button) {
        return button;
    }

    button = document.getElementById("download");

    if (button) {
        return button;
    }

    // Try common classes.

    button = document.querySelector(".download-btn");

    if (button) {
        return button;
    }

    button = document.querySelector(".download-button");

    if (button) {
        return button;
    }

    // Last fallback:
    // Look for a button containing Download.

    const buttons = document.querySelectorAll("button");

    for (const btn of buttons) {

        const text = (btn.textContent || "").toLowerCase();

        if (
            text.includes("download") ||
            text.includes("get file") ||
            text.includes("watch")
        ) {
            return btn;
        }
    }

    return null;
}


// ============================================================
// FIND ERROR ELEMENT
// ============================================================

function findErrorBox() {

    let element = document.getElementById("error");

    if (element) {
        return element;
    }

    element = document.getElementById("error-message");

    if (element) {
        return element;
    }

    element = document.querySelector(".error");

    if (element) {
        return element;
    }

    element = document.querySelector(".error-message");

    if (element) {
        return element;
    }

    return null;
}


// ============================================================
// FIND STATUS ELEMENT
// ============================================================

function findStatusBox() {

    let element = document.getElementById("status");

    if (element) {
        return element;
    }

    element = document.getElementById("status-message");

    if (element) {
        return element;
    }

    element = document.querySelector(".status");

    if (element) {
        return element;
    }

    element = document.querySelector(".status-message");

    if (element) {
        return element;
    }

    return null;
}


// ============================================================
// OPEN TELEGRAM BOT
// ============================================================

function openTelegramBot(code) {

    const telegramUrl =
        "https://t.me/" +
        TELEGRAM_BOT +
        "?start=" +
        encodeURIComponent(code);

    // Open Telegram bot.

    window.location.href = telegramUrl;
}


// ============================================================
// DOWNLOAD BUTTON ACTION
// ============================================================

function downloadFile(event) {

    // Prevent normal form/button behavior.

    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    hideError();
    hideStatus();

    const code = getDownloadCode();

    // No code in URL.

    if (!code) {

        showError(
            "Invalid download link. Please open the original download link again."
        );

        return false;
    }


    // Show a small status message if available.

    showStatus("Opening Telegram…");


    // Disable button temporarily.

    if (downloadButton) {

        downloadButton.disabled = true;

        const originalText = downloadButton.dataset.originalText;

        if (!originalText) {
            downloadButton.dataset.originalText =
                downloadButton.textContent;
        }

        downloadButton.textContent = "Opening Telegram...";
    }


    // Send the code to the Telegram bot.

    openTelegramBot(code);

    return false;
}


// ============================================================
// COPY CODE
// ============================================================

async function copyDownloadCode() {

    const code = getDownloadCode();

    if (!code) {
        showError("No download code found.");
        return;
    }

    try {

        await navigator.clipboard.writeText(code);

        showStatus("Download code copied.");

        setTimeout(function () {
            hideStatus();
        }, 2500);

    } catch (error) {

        showError("Unable to copy the download code.");

    }
}


// ============================================================
// DISPLAY DOWNLOAD CODE
// ============================================================

function displayDownloadCode() {

    const code = getDownloadCode();

    if (!code) {
        return;
    }

    // Possible code elements.

    const elements = [

        document.getElementById("download-code"),

        document.getElementById("code"),

        document.getElementById("file-code"),

        document.querySelector(".download-code"),

        document.querySelector(".file-code")

    ];

    for (const element of elements) {

        if (element) {
            element.textContent = code;
        }

    }
}


// ============================================================
// SETUP COPY BUTTON
// ============================================================

function setupCopyButton() {

    const copyButton =
        document.getElementById("copy-code") ||
        document.getElementById("copyCode") ||
        document.querySelector(".copy-code");

    if (!copyButton) {
        return;
    }

    copyButton.addEventListener("click", function (event) {

        event.preventDefault();

        copyDownloadCode();

    });
}


// ============================================================
// SETUP DOWNLOAD BUTTON
// ============================================================

function setupDownloadButton() {

    downloadButton = findDownloadButton();

    if (!downloadButton) {
        console.warn("Download button was not found.");
        return;
    }

    downloadButton.addEventListener(
        "click",
        downloadFile
    );
}


// ============================================================
// HANDLE ENTER KEY
// ============================================================

function setupKeyboardSupport() {

    document.addEventListener("keydown", function (event) {

        // Press Enter while focused on the download button.

        if (
            event.key === "Enter" &&
            document.activeElement === downloadButton
        ) {

            downloadFile(event);

        }

    });
}


// ============================================================
// INITIALIZE WEBSITE
// ============================================================

function initializePage() {

    errorBox = findErrorBox();

    statusBox = findStatusBox();

    displayDownloadCode();

    setupDownloadButton();

    setupCopyButton();

    setupKeyboardSupport();


    const code = getDownloadCode();

    if (!code) {

        console.warn(
            "No download code was found in the URL."
        );

    } else {

        console.log(
            "Download code detected:",
            code
        );

    }

}


// ============================================================
// START
// ============================================================

if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializePage
    );

} else {

    initializePage();

}
```
