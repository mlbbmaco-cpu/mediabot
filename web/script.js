"use strict";

const BOT_USERNAME = "walawwa_downloadBot";
const COUNTDOWN_SECONDS = 5;

let firstDownload = null;
let secondDownload = null;
let countdown = null;
let countdownNumber = null;
let message = null;
let fileInfo = null;
let countdownTimer = null;


function getDownloadCode() {
    const params = new URLSearchParams(window.location.search);

    let code = params.get("start");

    if (!code) {
        code = params.get("code");
    }

    if (!code) {
        return null;
    }

    code = code.trim();

    if (!code) {
        return null;
    }

    return code;
}


function makeTelegramLink(code) {
    return (
        "https://t.me/" +
        BOT_USERNAME +
        "?start=" +
        encodeURIComponent(code)
    );
}


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


function setupElements() {
    firstDownload = document.getElementById("firstDownload");
    secondDownload = document.getElementById("secondDownload");
    countdown = document.getElementById("countdown");
    countdownNumber = document.getElementById("countdownNumber");
    message = document.getElementById("message");
    fileInfo = document.getElementById("fileInfo");

    if (!firstDownload) {
        console.error("WALAWWA: firstDownload element not found.");
    }

    if (!secondDownload) {
        console.error("WALAWWA: secondDownload element not found.");
    }

    if (!countdown) {
        console.error("WALAWWA: countdown element not found.");
    }

    if (!countdownNumber) {
        console.error("WALAWWA: countdownNumber element not found.");
    }

    if (!message) {
        console.error("WALAWWA: message element not found.");
    }
}


function startCountdown(code) {
    if (
        !firstDownload ||
        !secondDownload ||
        !countdown ||
        !countdownNumber
    ) {
        console.error("WALAWWA: Required download elements are missing.");
        return;
    }

    if (!code) {
        showMessage("Invalid download link.", "error");
        return;
    }

    if (countdownTimer) {
        clearInterval(countdownTimer);
        countdownTimer = null;
    }

    firstDownload.disabled = true;
    firstDownload.style.display = "none";

    secondDownload.disabled = true;
    secondDownload.style.display = "none";

    countdown.style.display = "flex";

    let remaining = COUNTDOWN_SECONDS;

    countdownNumber.textContent = remaining;

    showMessage("Preparing your download...");

    countdownTimer = setInterval(function () {
        remaining--;

        if (remaining > 0) {
            countdownNumber.textContent = remaining;
            return;
        }

        clearInterval(countdownTimer);
        countdownTimer = null;

        countdown.style.display = "none";

        secondDownload.style.display = "flex";
        secondDownload.disabled = false;

        showMessage("Your download is ready.", "success");
    }, 1000);
}


function openTelegram(code) {
    if (!code) {
        showMessage("Invalid download link.", "error");
        return;
    }

    const telegramLink = makeTelegramLink(code);

    console.log("WALAWWA Telegram link:", telegramLink);

    showMessage("Opening Telegram...", "success");

    window.location.href = telegramLink;
}


function initializeDownloadPage() {
    setupElements();

    const code = getDownloadCode();

    console.log("WALAWWA website loaded.");
    console.log("Download code:", code);

    if (!code) {
        if (firstDownload) {
            firstDownload.disabled = true;
            firstDownload.textContent = "Invalid Download Link";
            firstDownload.style.opacity = "0.6";
        }

        showMessage(
            "Please open a valid WALAWWA download link.",
            "error"
        );

        return;
    }

    if (fileInfo) {
        fileInfo.style.display = "none";
    }

    if (!firstDownload || !secondDownload) {
        return;
    }

    firstDownload.style.display = "flex";
    firstDownload.disabled = false;

    secondDownload.style.display = "none";
    secondDownload.disabled = true;

    if (countdown) {
        countdown.style.display = "none";
    }

    firstDownload.onclick = function () {
        console.log("WALAWWA: Download button clicked.");

        if (firstDownload.disabled) {
            return;
        }

        startCountdown(code);
    };


    secondDownload.onclick = function () {
        console.log("WALAWWA: Continue Download button clicked.");

        if (secondDownload.disabled) {
            return;
        }

        secondDownload.disabled = true;

        openTelegram(code);
    };


    showMessage("Click Download to continue.");

    console.log("WALAWWA download page ready.");
    console.log("Telegram bot:", BOT_USERNAME);
}


if (document.readyState === "loading") {
    document.addEventListener(
        "DOMContentLoaded",
        initializeDownloadPage
    );
} else {
    initializeDownloadPage();
}
