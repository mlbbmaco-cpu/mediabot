"use strict";

const BOT_USERNAME = "walawwa_downloadBot";
const COUNTDOWN_SECONDS = 5;

let firstDownload;
let secondDownload;
let countdown;
let countdownNumber;
let message;


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


function showMessage(text, type) {
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

    console.log("WALAWWA JavaScript loaded.");

    firstDownload = document.getElementById("firstDownload");
    secondDownload = document.getElementById("secondDownload");
    countdown = document.getElementById("countdown");
    countdownNumber = document.getElementById("countdownNumber");
    message = document.getElementById("message");

    const code = getDownloadCode();

    console.log("Download code:", code);


    if (!firstDownload) {
        console.error("firstDownload not found");
        return;
    }

    if (!secondDownload) {
        console.error("secondDownload not found");
        return;
    }


    if (!code) {

        firstDownload.disabled = true;
        firstDownload.textContent = "Invalid Download Link";

        showMessage(
            "Please open a valid WALAWWA download link.",
            "error"
        );

        return;
    }


    firstDownload.onclick = function () {

        console.log("Download button clicked.");

        firstDownload.style.display = "none";

        countdown.style.display = "flex";

        let remaining = COUNTDOWN_SECONDS;

        countdownNumber.textContent = remaining;

        showMessage("Preparing your download...");


        const timer = setInterval(function () {

            remaining--;

            countdownNumber.textContent = remaining;


            if (remaining <= 0) {

                clearInterval(timer);

                countdown.style.display = "none";

                secondDownload.style.display = "flex";

                secondDownload.disabled = false;

                showMessage(
                    "Your download is ready.",
                    "success"
                );

            }

        }, 1000);

    };


    secondDownload.onclick = function () {

        console.log("Continue Download clicked.");

        secondDownload.disabled = true;

        showMessage(
            "Opening Telegram...",
            "success"
        );


        const telegramLink = makeTelegramLink(code);

        console.log(
            "Telegram URL:",
            telegramLink
        );


        window.location.href = telegramLink;

    };


    showMessage("Click Download to continue.");

    console.log("WALAWWA download page initialized.");
}


if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeDownloadPage
    );

} else {

    initializeDownloadPage();

}
