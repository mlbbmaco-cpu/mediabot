```javascript
// ============================================================
// WALAWWA WEB DOWNLOAD
// ============================================================
//
// FLOW:
//
// Telegram post
//      ↓
// https://walwwa.web.app/?start=CODE
//      ↓
// User opens website
//      ↓
// Presses FIRST "Download" button
//      ↓
// 5 second countdown
//      ↓
// SECOND "Download" button appears
//      ↓
// User presses SECOND "Download"
//      ↓
// Telegram bot opens:
//
// https://t.me/walawwa_downloadBot?start=CODE
//
//      ↓
// Bot receives CODE
//      ↓
// Bot finds the stored Telegram message
//      ↓
// Bot sends the video to the user
//
// IMPORTANT:
// The website does NOT download the video.
// The video remains stored in Telegram.
// ============================================================


const TELEGRAM_BOT = "walawwa_downloadBot";


// ============================================================
// SETTINGS
// ============================================================

const COUNTDOWN_SECONDS = 5;


// ============================================================
// VARIABLES
// ============================================================

let downloadButton = null;
let secondDownloadButton = null;
let countdownElement = null;
let errorBox = null;
let statusBox = null;

let countdownRunning = false;
let countdownFinished = false;


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

    } else {

        alert(message);

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
// FIND ERROR BOX
// ============================================================

function findErrorBox() {

    let element =
        document.getElementById("error");

    if (element) {
        return element;
    }


    element =
        document.getElementById("error-message");

    if (element) {
        return element;
    }


    element =
        document.querySelector(".error");

    if (element) {
        return element;
    }


    element =
        document.querySelector(".error-message");

    if (element) {
        return element;
    }


    return null;
}


// ============================================================
// FIND STATUS BOX
// ============================================================

function findStatusBox() {

    let element =
        document.getElementById("status");

    if (element) {
        return element;
    }


    element =
        document.getElementById("status-message");

    if (element) {
        return element;
    }


    element =
        document.querySelector(".status");

    if (element) {
        return element;
    }


    element =
        document.querySelector(".status-message");

    if (element) {
        return element;
    }


    return null;
}


// ============================================================
// FIND FIRST DOWNLOAD BUTTON
// ============================================================

function findDownloadButton() {

    let button =
        document.getElementById("download-btn");

    if (button) {
        return button;
    }


    button =
        document.getElementById("downloadButton");

    if (button) {
        return button;
    }


    button =
        document.getElementById("download");

    if (button) {
        return button;
    }


    button =
        document.querySelector(".download-btn");

    if (button) {
        return button;
    }


    button =
        document.querySelector(".download-button");

    if (button) {
        return button;
    }


    // Fallback: find a button containing Download.

    const buttons =
        document.querySelectorAll("button");


    for (const buttonElement of buttons) {

        const text =
            (buttonElement.textContent || "")
            .toLowerCase();


        if (
            text.includes("download") ||
            text.includes("get file")
        ) {

            return buttonElement;

        }

    }


    return null;
}


// ============================================================
// CREATE SECOND DOWNLOAD BUTTON
// ============================================================

function createSecondDownloadButton() {

    // If it already exists, don't create another one.

    if (secondDownloadButton) {
        return secondDownloadButton;
    }


    // Create button.

    const button =
        document.createElement("button");


    button.type = "button";

    button.id =
        "second-download-btn";

    button.className =
        "download-button second-download-button";


    button.textContent =
        "Download";


    // Hide initially.

    button.style.display =
        "none";


    // Basic styling so it works even without CSS changes.

    button.style.cursor =
        "pointer";


    button.style.padding =
        "12px 24px";


    button.style.marginTop =
        "15px";


    // Put it after the first button.

    if (downloadButton &&
        downloadButton.parentNode) {

        downloadButton.parentNode.insertBefore(
            button,
            downloadButton.nextSibling
        );

    } else {

        document.body.appendChild(button);

    }


    secondDownloadButton =
        button;


    // Add click event.

    button.addEventListener(
        "click",
        openTelegramDownload
    );


    return button;
}


// ============================================================
// CREATE COUNTDOWN ELEMENT
// ============================================================

function createCountdownElement() {

    if (countdownElement) {
        return countdownElement;
    }


    const element =
        document.createElement("div");


    element.id =
        "download-countdown";


    element.className =
        "download-countdown";


    element.style.display =
        "none";


    element.style.marginTop =
        "15px";


    element.style.fontSize =
        "18px";


    element.style.fontWeight =
        "bold";


    element.textContent =
        "Please wait...";


    // Put after first button.

    if (downloadButton &&
        downloadButton.parentNode) {

        downloadButton.parentNode.insertBefore(
            element,
            downloadButton.nextSibling
        );

    } else {

        document.body.appendChild(element);

    }


    countdownElement =
        element;


    return element;
}


// ============================================================
// FIRST DOWNLOAD BUTTON
// ============================================================
//
// User presses this button.
// It DOES NOT open Telegram yet.
//
// It starts the 5-second countdown.
// ============================================================

function startCountdown(event) {

    if (event) {

        event.preventDefault();
        event.stopPropagation();

    }


    // Don't allow countdown twice.

    if (countdownRunning) {
        return false;
    }


    // Already finished.

    if (countdownFinished) {
        return false;
    }


    hideError();
    hideStatus();


    // Check code.

    const code =
        getDownloadCode();


    if (!code) {

        showError(
            "Invalid or missing download link."
        );

        return false;

    }


    countdownRunning = true;


    // Make sure countdown element exists.

    createCountdownElement();

    createSecondDownloadButton();


    // Hide second button.

    secondDownloadButton.style.display =
        "none";


    // Disable first button.

    if (downloadButton) {

        downloadButton.disabled =
            true;

        downloadButton.style.cursor =
            "default";

    }


    // Start at 5.

    let seconds =
        COUNTDOWN_SECONDS;


    countdownElement.style.display =
        "block";


    countdownElement.textContent =
        "Please wait " +
        seconds +
        " seconds...";


    // Countdown timer.

    const timer =
        setInterval(function () {

            seconds--;


            if (seconds > 0) {

                countdownElement.textContent =
                    "Please wait " +
                    seconds +
                    " seconds...";

                return;

            }


            // Countdown finished.

            clearInterval(timer);


            countdownRunning =
                false;

            countdownFinished =
                true;


            // Hide countdown.

            countdownElement.style.display =
                "none";


            // Hide first button.

            if (downloadButton) {

                downloadButton.style.display =
                    "none";

            }


            // Show second button.

            secondDownloadButton.style.display =
                "inline-block";


            secondDownloadButton.disabled =
                false;


            secondDownloadButton.textContent =
                "Download";


            showStatus(
                "Your download is ready."
            );


        }, 1000);


    return false;
}


// ============================================================
// OPEN TELEGRAM DOWNLOAD
// ============================================================
//
// This is the SECOND button.
//
// It opens:
// https://t.me/walawwa_downloadBot?start=CODE
//
// The bot handles the actual file delivery.
// ============================================================

function openTelegramDownload(event) {

    if (event) {

        event.preventDefault();
        event.stopPropagation();

    }


    hideError();


    const code =
        getDownloadCode();


    if (!code) {

        showError(
            "Invalid or missing download code."
        );

        return false;

    }


    // Telegram deep link.

    const telegramUrl =
        "https://t.me/" +
        TELEGRAM_BOT +
        "?start=" +
        encodeURIComponent(code);


    // Update button.

    if (secondDownloadButton) {

        secondDownloadButton.disabled =
            true;

        secondDownloadButton.textContent =
            "Opening Telegram...";

    }


    showStatus(
        "Opening Telegram..."
    );


    // Open Telegram.

    window.location.href =
        telegramUrl;


    return false;
}


// ============================================================
// DISPLAY DOWNLOAD CODE
// ============================================================

function displayDownloadCode() {

    const code =
        getDownloadCode();


    if (!code) {
        return;
    }


    const elements = [

        document.getElementById(
            "download-code"
        ),

        document.getElementById(
            "code"
        ),

        document.getElementById(
            "file-code"
        ),

        document.querySelector(
            ".download-code"
        ),

        document.querySelector(
            ".file-code"
        )

    ];


    for (const element of elements) {

        if (element) {

            element.textContent =
                code;

        }

    }

}


// ============================================================
// COPY DOWNLOAD CODE
// ============================================================

async function copyDownloadCode() {

    const code =
        getDownloadCode();


    if (!code) {

        showError(
            "No download code found."
        );

        return;

    }


    try {

        await navigator.clipboard.writeText(
            code
        );


        showStatus(
            "Download code copied."
        );


        setTimeout(function () {

            hideStatus();

        }, 2500);


    } catch (error) {

        showError(
            "Unable to copy the download code."
        );

    }

}


// ============================================================
// SETUP COPY BUTTON
// ============================================================

function setupCopyButton() {

    const copyButton =
        document.getElementById(
            "copy-code"
        ) ||
        document.getElementById(
            "copyCode"
        ) ||
        document.querySelector(
            ".copy-code"
        );


    if (!copyButton) {
        return;
    }


    copyButton.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            copyDownloadCode();

        }
    );

}


// ============================================================
// SETUP DOWNLOAD SYSTEM
// ============================================================

function setupDownloadSystem() {

    // Find existing first button.

    downloadButton =
        findDownloadButton();


    if (!downloadButton) {

        console.warn(
            "Download button was not found."
        );

        return;

    }


    // Create countdown.

    createCountdownElement();


    // Create second button.

    createSecondDownloadButton();


    // First button starts countdown.

    downloadButton.addEventListener(
        "click",
        startCountdown
    );


    // Second button opens Telegram.

    // Already connected inside
    // createSecondDownloadButton().

}


// ============================================================
// KEYBOARD SUPPORT
// ============================================================

function setupKeyboardSupport() {

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                document.activeElement ===
                downloadButton
            ) {

                startCountdown(event);

            }

        }
    );

}


// ============================================================
// INITIALIZE PAGE
// ============================================================

function initializePage() {

    // Find page elements.

    errorBox =
        findErrorBox();


    statusBox =
        findStatusBox();


    // Show code if available.

    displayDownloadCode();


    // Setup download system.

    setupDownloadSystem();


    // Setup copy button.

    setupCopyButton();


    // Keyboard support.

    setupKeyboardSupport();


    // Check URL.

    const code =
        getDownloadCode();


    if (!code) {

        console.warn(
            "No download code found in URL."
        );

    } else {

        console.log(
            "WALAWWA download code detected:",
            code
        );

    }

}


// ============================================================
// START APPLICATION
// ============================================================

if (
    document.readyState === "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializePage
    );

} else {

    initializePage();

}
```
