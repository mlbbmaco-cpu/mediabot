```javascript
"use strict";

/*
 * WALAWWA WEBSITE
 *
 * Flow:
 *
 * Website
 *   ↓
 * First Download button
 *   ↓
 * 5 second countdown
 *   ↓
 * Second Download button
 *   ↓
 * Telegram Bot deep link
 *   ↓
 * Bot receives CODE
 *   ↓
 * Bot sends the stored Telegram file
 *
 * IMPORTANT:
 * This JavaScript does NOT download the video.
 * It does NOT use Northflank.
 * It does NOT store the video.
 */

const BOT_USERNAME = "walawwa_downloadBot";
const COUNTDOWN_SECONDS = 5;


// ----------------------------------------------------
// GET CODE FROM URL
// ----------------------------------------------------

function getDownloadCode() {
    const params = new URLSearchParams(window.location.search);

    let code = params.get("start");

    if (!code) {
        code = params.get("code");
    }

    if (!code) {
        return null;
    }

    return code.trim();
}


// ----------------------------------------------------
// TELEGRAM LINK
// ----------------------------------------------------

function makeTelegramLink(code) {
    return `https://t.me/${BOT_USERNAME}?start=${encodeURIComponent(code)}`;
}


// ----------------------------------------------------
// ELEMENTS
// ----------------------------------------------------

let firstDownload;
let secondDownload;
let countdown;
let countdownNumber;
let message;
let fileInfo;


// ----------------------------------------------------
// SHOW MESSAGE
// ----------------------------------------------------

function showMessage(text, type = "") {
    if (!message) {
        return;
    }

    message.textContent = text;
    message.className = "message";

    if (type) {
        message.classList.add(type);
    }
}


// ----------------------------------------------------
// CREATE / FIND DOWNLOAD UI
// ----------------------------------------------------

function setupElements() {

    firstDownload = document.getElementById("firstDownload");
    secondDownload = document.getElementById("secondDownload");
    countdown = document.getElementById("countdown");
    countdownNumber = document.getElementById("countdownNumber");
    message = document.getElementById("message");
    fileInfo = document.getElementById("fileInfo");

    const downloadArea = document.getElementById("downloadArea");

    if (!downloadArea) {
        console.error("WALAWWA: #downloadArea was not found.");
        return;
    }


    // ---------------------------------------------
    // FIRST BUTTON
    // ---------------------------------------------

    if (!firstDownload) {

        firstDownload = document.createElement("button");

        firstDownload.id = "firstDownload";
        firstDownload.className = "download-button";
        firstDownload.type = "button";
        firstDownload.textContent = "⬇️ Download";

        downloadArea.insertBefore(
            firstDownload,
            downloadArea.firstChild
        );
    }


    // ---------------------------------------------
    // COUNTDOWN
    // ---------------------------------------------

    if (!countdown) {

        countdown = document.createElement("div");

        countdown.id = "countdown";
        countdown.className = "countdown";
        countdown.style.display = "none";

        countdown.innerHTML =
            `Please wait <span id="countdownNumber" class="countdown-number">${COUNTDOWN_SECONDS}</span> seconds...`;

        downloadArea.appendChild(countdown);
    }


    countdownNumber =
        document.getElementById("countdownNumber");


    // ---------------------------------------------
    // SECOND BUTTON
    // ---------------------------------------------

    if (!secondDownload) {

        secondDownload = document.createElement("button");

        secondDownload.id = "secondDownload";
        secondDownload.className = "download-button";
        secondDownload.type = "button";
        secondDownload.textContent = "⬇️ Continue Download";
        secondDownload.style.display = "none";

        downloadArea.appendChild(secondDownload);
    }


    // ---------------------------------------------
    // MESSAGE
    // ---------------------------------------------

    if (!message) {

        message = document.createElement("div");

        message.id = "message";
        message.className = "message";

        downloadArea.appendChild(message);
    }
}


// ----------------------------------------------------
// START COUNTDOWN
// ----------------------------------------------------

function startCountdown(code) {

    if (
        !firstDownload ||
        !secondDownload ||
        !countdown ||
        !countdownNumber
    ) {
        console.error(
            "WALAWWA: Download elements are missing."
        );

        return;
    }


    // Disable first button

    firstDownload.disabled = true;


    // Hide first button

    firstDownload.style.display = "none";


    // Show countdown

    countdown.style.display = "flex";


    // Hide second button

    secondDownload.style.display = "none";


    let remaining = COUNTDOWN_SECONDS;

    countdownNumber.textContent = remaining;


    showMessage(
        "Preparing your download...",
        ""
    );


    const timer = setInterval(() => {

        remaining--;


        if (remaining > 0) {

            countdownNumber.textContent =
                remaining;

            return;
        }


        clearInterval(timer);


        countdown.style.display = "none";


        secondDownload.style.display =
            "flex";


        secondDownload.disabled = false;


        showMessage(
            "Your download is ready.",
            "success"
        );

    }, 1000);
}


// ----------------------------------------------------
// OPEN TELEGRAM
// ----------------------------------------------------

function openTelegram(code) {

    if (!code) {

        showMessage(
            "Invalid download link.",
            "error"
        );

        return;
    }


    const telegramLink =
        makeTelegramLink(code);


    showMessage(
        "Opening Telegram...",
        "success"
    );


    /*
     * The Telegram bot receives:
     *
     * /start CODE
     *
     * The bot then finds the stored Telegram
     * message and sends the file.
     */

    window.location.href = telegramLink;
}


// ----------------------------------------------------
// INITIALIZE
// ----------------------------------------------------

function initializeDownloadPage() {

    setupElements();


    const code = getDownloadCode();


    // ---------------------------------------------
    // NO CODE
    // ---------------------------------------------

    if (!code) {

        if (firstDownload) {

            firstDownload.disabled = true;

            firstDownload.textContent =
                "Invalid Download Link";

            firstDownload.style.opacity =
                "0.6";
        }


        showMessage(
            "Please open a valid WALAWWA download link.",
            "error"
        );

        return;
    }


    // ---------------------------------------------
    // OPTIONAL FILE INFO
    // ---------------------------------------------

    if (fileInfo) {
        fileInfo.style.display = "none";
    }


    // ---------------------------------------------
    // FIRST DOWNLOAD
    // ---------------------------------------------

    firstDownload.onclick = function () {

        if (firstDownload.disabled) {
            return;
        }


        startCountdown(code);
    };


    // ---------------------------------------------
    // SECOND DOWNLOAD
    // ---------------------------------------------

    secondDownload.onclick = function () {

        if (secondDownload.disabled) {
            return;
        }


        secondDownload.disabled = true;


        openTelegram(code);
    };


    // ---------------------------------------------
    // INITIAL STATE
    // ---------------------------------------------

    firstDownload.style.display =
        "flex";

    firstDownload.disabled =
        false;

    secondDownload.style.display =
        "none";

    secondDownload.disabled =
        true;

    countdown.style.display =
        "none";


    showMessage(
        "Click Download to continue.",
        ""
    );


    // ---------------------------------------------
    // DEBUG INFORMATION
    // ---------------------------------------------

    console.log(
        "WALAWWA download page ready."
    );

    console.log(
        "Download code:",
        code
    );

    console.log(
        "Telegram bot:",
        BOT_USERNAME
    );
}


// ----------------------------------------------------
// START WHEN PAGE LOADS
// ----------------------------------------------------

if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeDownloadPage
    );

} else {

    initializeDownloadPage();
}
```
