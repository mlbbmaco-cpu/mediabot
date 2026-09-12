"use strict";

/*

* WALAWWA WEBSITE
*
* Flow:
* Website
* ↓
* Download button
* ↓
* 5 second countdown
* ↓
* Continue Download button
* ↓
* Telegram Bot deep link
* ↓
* Bot receives CODE
* ↓
* Bot sends the stored Telegram file
*
* This website does NOT download or store the video.
  */

const BOT_USERNAME = "walawwa_downloadBot";
const COUNTDOWN_SECONDS = 5;

let firstDownload = null;
let secondDownload = null;
let countdown = null;
let countdownNumber = null;
let message = null;
let fileInfo = null;
let countdownTimer = null;

// ----------------------------------------------------
// GET DOWNLOAD CODE
// ----------------------------------------------------

function getDownloadCode() {
const params = new URLSearchParams(window.location.search);

```
const startCode = params.get("start");
const normalCode = params.get("code");

const code = startCode || normalCode;

if (!code) {
    return null;
}

const cleanedCode = code.trim();

return cleanedCode || null;
```

}

// ----------------------------------------------------
// CREATE TELEGRAM LINK
// ----------------------------------------------------

function makeTelegramLink(code) {
return "https://t.me/" +
BOT_USERNAME +
"?start=" +
encodeURIComponent(code);
}

// ----------------------------------------------------
// SHOW MESSAGE
// ----------------------------------------------------

function showMessage(text, type = "") {
if (!message) {
return;
}

```
message.textContent = text;
message.className = "message";

if (type) {
    message.classList.add(type);
}
```

}

// ----------------------------------------------------
// FIND PAGE ELEMENTS
// ----------------------------------------------------

function setupElements() {

```
firstDownload =
    document.getElementById("firstDownload");

secondDownload =
    document.getElementById("secondDownload");

countdown =
    document.getElementById("countdown");

countdownNumber =
    document.getElementById("countdownNumber");

message =
    document.getElementById("message");

fileInfo =
    document.getElementById("fileInfo");

const downloadArea =
    document.getElementById("downloadArea");


if (!downloadArea) {
    console.error(
        "WALAWWA: #downloadArea was not found."
    );

    return false;
}


// ------------------------------------------------
// CREATE FIRST BUTTON IF MISSING
// ------------------------------------------------

if (!firstDownload) {

    firstDownload =
        document.createElement("button");

    firstDownload.id =
        "firstDownload";

    firstDownload.className =
        "download-button";

    firstDownload.type =
        "button";

    firstDownload.textContent =
        "⬇️ Download";

    downloadArea.insertBefore(
        firstDownload,
        downloadArea.firstChild
    );
}


// ------------------------------------------------
// CREATE COUNTDOWN IF MISSING
// ------------------------------------------------

if (!countdown) {

    countdown =
        document.createElement("div");

    countdown.id =
        "countdown";

    countdown.className =
        "countdown";

    countdown.style.display =
        "none";

    countdown.innerHTML =
        'Please wait <span id="countdownNumber" ' +
        'class="countdown-number">' +
        COUNTDOWN_SECONDS +
        '</span> seconds...';

    downloadArea.appendChild(
        countdown
    );
}


countdownNumber =
    document.getElementById(
        "countdownNumber"
    );


// ------------------------------------------------
// CREATE SECOND BUTTON IF MISSING
// ------------------------------------------------

if (!secondDownload) {

    secondDownload =
        document.createElement("button");

    secondDownload.id =
        "secondDownload";

    secondDownload.className =
        "download-button";

    secondDownload.type =
        "button";

    secondDownload.textContent =
        "⬇️ Continue Download";

    secondDownload.style.display =
        "none";

    downloadArea.appendChild(
        secondDownload
    );
}


// ------------------------------------------------
// CREATE MESSAGE IF MISSING
// ------------------------------------------------

if (!message) {

    message =
        document.createElement("div");

    message.id =
        "message";

    message.className =
        "message";

    downloadArea.appendChild(
        message
    );
}


return true;
```

}

// ----------------------------------------------------
// START COUNTDOWN
// ----------------------------------------------------

function startCountdown(code) {

```
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


if (!code) {

    showMessage(
        "Invalid download link.",
        "error"
    );

    return;
}


// Prevent multiple timers.

if (countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = null;
}


// Disable first button.

firstDownload.disabled = true;

firstDownload.style.display =
    "none";


// Show countdown.

countdown.style.display =
    "flex";


// Hide second button.

secondDownload.style.display =
    "none";

secondDownload.disabled =
    true;


let remaining =
    COUNTDOWN_SECONDS;

countdownNumber.textContent =
    remaining;


showMessage(
    "Preparing your download...",
    ""
);


countdownTimer =
    setInterval(function () {

        remaining--;


        if (remaining > 0) {

            countdownNumber.textContent =
                remaining;

            return;
        }


        clearInterval(
            countdownTimer
        );

        countdownTimer =
            null;


        countdown.style.display =
            "none";


        secondDownload.style.display =
            "flex";

        secondDownload.disabled =
            false;


        showMessage(
            "Your download is ready.",
            "success"
        );

    }, 1000);
```

}

// ----------------------------------------------------
// OPEN TELEGRAM
// ----------------------------------------------------

function openTelegram(code) {

```
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


// Send the user to:
// https://t.me/walawwa_downloadBot?start=CODE

window.location.href =
    telegramLink;
```

}

// ----------------------------------------------------
// INITIALIZE PAGE
// ----------------------------------------------------

function initializeDownloadPage() {

```
console.log(
    "WALAWWA: Initializing..."
);


const elementsReady =
    setupElements();


if (!elementsReady) {
    return;
}


const code =
    getDownloadCode();


// ------------------------------------------------
// INVALID / MISSING CODE
// ------------------------------------------------

if (!code) {

    firstDownload.disabled =
        true;

    firstDownload.textContent =
        "Invalid Download Link";

    firstDownload.style.opacity =
        "0.6";

    secondDownload.style.display =
        "none";

    countdown.style.display =
        "none";


    showMessage(
        "Please open a valid WALAWWA download link.",
        "error"
    );


    console.error(
        "WALAWWA: No download code found."
    );

    return;
}


// ------------------------------------------------
// OPTIONAL FILE INFO
// ------------------------------------------------

if (fileInfo) {

    fileInfo.style.display =
        "none";
}


// ------------------------------------------------
// FIRST BUTTON
// ------------------------------------------------

firstDownload.onclick =
    function () {

        if (
            firstDownload.disabled
        ) {
            return;
        }

        startCountdown(code);
    };


// ------------------------------------------------
// SECOND BUTTON
// ------------------------------------------------

secondDownload.onclick =
    function () {

        if (
            secondDownload.disabled
        ) {
            return;
        }


        secondDownload.disabled =
            true;


        openTelegram(code);
    };


// ------------------------------------------------
// INITIAL STATE
// ------------------------------------------------

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


// ------------------------------------------------
// DEBUG
// ------------------------------------------------

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
```

}

// ----------------------------------------------------
// START PAGE
// ----------------------------------------------------

if (
document.readyState ===
"loading"
) {

```
document.addEventListener(
    "DOMContentLoaded",
    initializeDownloadPage
);
```

} else {

```
initializeDownloadPage();
```

}
