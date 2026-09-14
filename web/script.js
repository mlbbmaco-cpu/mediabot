"use strict";

const BOT_USERNAME = "walawwa_downloadBot";
const COUNTDOWN_SECONDS = 5;

let firstDownload = null;
let secondDownload = null;
let countdown = null;
let countdownNumber = null;
let message = null;

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


    /* =========================
       INITIAL PAGE STATE
    ========================= */

    // Countdown MUST be hidden when page opens.
    countdown.style.display = "none";

    // Download button MUST be hidden initially.
    secondDownload.style.display = "none";

    secondDownload.disabled = true;

    // Continue button is visible.
    firstDownload.style.display = "flex";

    firstDownload.disabled = false;

    showMessage("");


    /* =========================
       GET DOWNLOAD CODE
    ========================= */

    const code = getDownloadCode();

    console.log(
        "WALAWWA: Download code =",
        code
    );


    if (!code) {

        firstDownload.disabled = true;

        firstDownload.innerHTML =
            '<span class="download-icon">!</span>' +
            '<span class="button-text">' +
            'Invalid Download Link' +
            '</span>';

        showMessage(
            "Please open a valid WALAWWA download link.",
            "error"
        );

        return;
    }


    /* =========================
       CONTINUE DOWNLOAD
    ========================= */

    firstDownload.addEventListener(
        "click",
        function () {

            console.log(
                "WALAWWA: Continue Download clicked"
            );


            /* Stop any old timer */
            if (countdownTimer) {
                clearInterval(countdownTimer);
                countdownTimer = null;
            }


            /* Hide Continue button */
            firstDownload.style.display = "none";

            firstDownload.disabled = true;


            /* Hide final Download button */
            secondDownload.style.display = "none";

            secondDownload.disabled = true;


            /* Show countdown */
            countdown.style.display = "flex";


            /* Start at 5 */
            let remaining = COUNTDOWN_SECONDS;

            countdownNumber.textContent = remaining;

            showMessage("");


            /* =========================
               COUNTDOWN
            ========================= */

            countdownTimer = setInterval(
                function () {

                    remaining--;

                    /*
                       Show:
                       5
                       4
                       3
                       2
                       1
                    */

                    if (remaining > 0) {

                        countdownNumber.textContent =
                            remaining;

                        return;
                    }


                    /* =========================
                       COUNTDOWN FINISHED
                    ========================= */

                    clearInterval(countdownTimer);

                    countdownTimer = null;


                    /* Hide countdown */
                    countdown.style.display = "none";


                    /* Show Download button */
                    secondDownload.style.display = "flex";

                    secondDownload.disabled = false;


                    console.log(
                        "WALAWWA: Download button ready"
                    );

                },
                1000
            );
        }
    );


    /* =========================
       DOWNLOAD BUTTON
    ========================= */

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


            window.location.href =
                telegramLink;
        }
    );
}


/* =========================
   START
========================= */

if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeDownloadPage
    );

} else {

    initializeDownloadPage();

}
