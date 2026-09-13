"use strict";

const BOT_USERNAME = "walawwa_downloadBot";
const COUNTDOWN_SECONDS = 5;

document.addEventListener("DOMContentLoaded", function () {

```
const firstDownload = document.getElementById("firstDownload");
const secondDownload = document.getElementById("secondDownload");
const countdown = document.getElementById("countdown");
const countdownNumber = document.getElementById("countdownNumber");
const message = document.getElementById("message");

console.log("WALAWWA JavaScript loaded");

if (
    !firstDownload ||
    !secondDownload ||
    !countdown ||
    !countdownNumber
) {
    console.error("WALAWWA: required elements missing");
    return;
}

const params = new URLSearchParams(window.location.search);

let code = params.get("start");

if (!code) {
    code = params.get("code");
}

if (code) {
    code = code.trim();
}

console.log("Download code:", code);

if (!code) {
    firstDownload.disabled = true;
    firstDownload.innerHTML = "<span>Invalid Download Link</span>";

    if (message) {
        message.textContent =
            "Please open a valid WALAWWA download link.";
        message.className = "message error";
    }

    return;
}

firstDownload.style.display = "flex";
firstDownload.disabled = false;

secondDownload.style.display = "none";
secondDownload.disabled = true;

countdown.style.display = "none";

firstDownload.addEventListener("click", function () {

    console.log("Continue Download clicked");

    firstDownload.style.display = "none";
    firstDownload.disabled = true;

    countdown.style.display = "flex";

    let remaining = COUNTDOWN_SECONDS;

    countdownNumber.textContent = remaining;

    const timer = setInterval(function () {

        remaining--;

        countdownNumber.textContent = remaining;

        if (remaining <= 0) {

            clearInterval(timer);

            countdown.style.display = "none";

            secondDownload.style.display = "flex";
            secondDownload.disabled = false;

            console.log("Download button ready");
        }

    }, 1000);

});

secondDownload.addEventListener("click", function () {

    console.log("Download clicked");

    secondDownload.disabled = true;

    const telegramLink =
        "https://t.me/" +
        BOT_USERNAME +
        "?start=" +
        encodeURIComponent(code);

    console.log("Opening Telegram:", telegramLink);

    window.location.href = telegramLink;

});
```

});
