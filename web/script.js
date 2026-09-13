"use strict";

const BOT_USERNAME = "walawwa_downloadBot";
const COUNTDOWN_SECONDS = 5;

let firstDownload = null;
let secondDownload = null;
let countdown = null;
let countdownNumber = null;
let message = null;

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

    return code || null;
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

function initializeDownloadPage() {
    console.log("WALAWWA: JavaScript loaded");

    firstDownload = document.getElementById("firstDownload");
    secondDownload = document.getElementById("secondDownload");
    countdown = document.getElementById("countdown");
    countdownNumber = document.getElementById("countdownNumber");
    message = document.getElementById("message");

    if (
        !firstDownload ||
        !secondDownload ||
        !countdown ||
        !countdownNumber ||
        !message
    ) {
        console.error(
            "WALAWWA: Required HTML elements are missing."
        );
        return;
    }

    const code = getDownloadCode();

    console.log(
        "WALAWWA: Download code =",
        code
    );

    if (!code) {
        firstDownload.disabled = true;

        firstDownload.innerHTML =
            '<span class="download-icon">!</span>' +
            '<span>Invalid Download Link</span>';

        showMessage(
            "Please open a valid WALAWWA download link.",
            "error"
        );

        return;
    }

    firstDownload.style.display = "flex";
    firstDownload.disabled = false;

    secondDownload.style.display = "none";
    secondDownload.disabled = true;

    countdown.style.display = "none";

    showMessage("");

    firstDownload.addEventListener(
        "click",
        function () {
            console.log(
                "WALAWWA: Continue Download clicked"
            );

            firstDownload.style.display = "none";
            firstDownload.disabled = true;

            countdown.style.display = "flex";

            let remaining = COUNTDOWN_SECONDS;

            countdownNumber.textContent = remaining;

            showMessage("");

            const timer = setInterval(
                function () {
                    remaining--;

                    countdownNumber.textContent =
                        remaining;

                    if (remaining <= 0) {
                        clearInterval(timer);

                        countdown.style.display = "none";

                        secondDownload.style.display =
                            "flex";

                        secondDownload.disabled = false;

                        console.log(
                            "WALAWWA: Download button ready"
                        );
                    }
                },
                1000
            );
        }
    );

    secondDownload.addEventListener(
        "click",
        function () {
            console.log(
                "WALAWWA: Download clicked"
            );

            secondDownload.disabled = true;

            const telegramLink =
                makeTelegramLink(code);

            console.log(
                "WALAWWA: Opening Telegram:",
                telegramLink
            );

            window.location.href = telegramLink;
        }
    );
}

if (document.readyState === "loading") {
    document.addEventListener(
        "DOMContentLoaded",
        initializeDownloadPage
    );
} else {
    initializeDownloadPage();
}
