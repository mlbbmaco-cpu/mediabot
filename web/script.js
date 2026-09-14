"use strict";


/* =========================================================
   SETTINGS
========================================================= */

const BOT_USERNAME = "walawwa_downloadBot";

const COUNTDOWN_SECONDS = 5;


/* =========================================================
   ELEMENTS
========================================================= */

let firstDownload = null;

let secondDownload = null;

let countdown = null;

let countdownNumber = null;

let message = null;


/* =========================================================
   TIMER
========================================================= */

let countdownTimer = null;


/* =========================================================
   GET DOWNLOAD CODE
========================================================= */

function getDownloadCode() {

    const params =
        new URLSearchParams(
            window.location.search
        );


    let code =
        params.get("start");


    if (!code) {

        code =
            params.get("code");
    }


    if (!code) {

        return null;
    }


    code =
        code.trim();


    return code || null;
}


/* =========================================================
   TELEGRAM LINK
========================================================= */

function makeTelegramLink(code) {

    return (
        "https://t.me/" +
        BOT_USERNAME +
        "?start=" +
        encodeURIComponent(code)
    );
}


/* =========================================================
   MESSAGE
========================================================= */

function showMessage(text, type = "") {

    if (!message) {

        return;
    }


    message.textContent =
        text;


    message.className =
        "message";


    if (type) {

        message.classList.add(type);
    }
}


/* =========================================================
   HIDE COUNTDOWN
========================================================= */

function hideCountdown() {

    if (!countdown) {

        return;
    }


    countdown.classList.remove(
        "countdown-active"
    );


    countdown.setAttribute(
        "aria-hidden",
        "true"
    );
}


/* =========================================================
   SHOW COUNTDOWN
========================================================= */

function showCountdown() {

    if (!countdown) {

        return;
    }


    countdown.classList.add(
        "countdown-active"
    );


    countdown.setAttribute(
        "aria-hidden",
        "false"
    );
}


/* =========================================================
   INITIALIZE
========================================================= */

function initializeDownloadPage() {

    console.log(
        "WALAWWA: JavaScript loaded"
    );


    /* =====================================================
       GET HTML ELEMENTS
    ===================================================== */

    firstDownload =
        document.getElementById(
            "firstDownload"
        );


    secondDownload =
        document.getElementById(
            "secondDownload"
        );


    countdown =
        document.getElementById(
            "countdown"
        );


    countdownNumber =
        document.getElementById(
            "countdownNumber"
        );


    message =
        document.getElementById(
            "message"
        );


    /* =====================================================
       CHECK ELEMENTS
    ===================================================== */

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


    /* =====================================================
       FORCE INITIAL STATE
       
       THIS IS IMPORTANT.
       
       Countdown is NEVER visible when page opens.
    ===================================================== */

    hideCountdown();


    firstDownload.style.display =
        "flex";

    firstDownload.disabled =
        false;


    secondDownload.style.display =
        "none";

    secondDownload.disabled =
        true;


    countdownNumber.textContent =
        COUNTDOWN_SECONDS;


    showMessage("");


    /* =====================================================
       GET CODE
    ===================================================== */

    const code =
        getDownloadCode();


    console.log(
        "WALAWWA: Download code =",
        code
    );


    /* =====================================================
       INVALID LINK
    ===================================================== */

    if (!code) {

        firstDownload.disabled =
            true;


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


    /* =====================================================
       CONTINUE DOWNLOAD CLICK
    ===================================================== */

    firstDownload.addEventListener(
        "click",
        function () {

            console.log(
                "WALAWWA: Continue Download clicked"
            );


            /* =============================================
               STOP OLD TIMER
            ============================================= */

            if (countdownTimer) {

                clearInterval(
                    countdownTimer
                );

                countdownTimer =
                    null;
            }


            /* =============================================
               HIDE CONTINUE BUTTON
            ============================================= */

            firstDownload.style.display =
                "none";

            firstDownload.disabled =
                true;


            /* =============================================
               HIDE DOWNLOAD BUTTON
            ============================================= */

            secondDownload.style.display =
                "none";

            secondDownload.disabled =
                true;


            /* =============================================
               START AT 5
            ============================================= */

            let remaining =
                COUNTDOWN_SECONDS;


            countdownNumber.textContent =
                remaining;


            /* =============================================
               SHOW COUNTDOWN
            ============================================= */

            showCountdown();


            showMessage("");


            /* =============================================
               COUNTDOWN
               
               5
               4
               3
               2
               1
               
               Then Download button.
            ============================================= */

            countdownTimer =
                setInterval(
                    function () {

                        remaining--;


                        if (remaining > 0) {

                            countdownNumber.textContent =
                                remaining;

                            return;
                        }


                        /* =================================
                           COUNTDOWN FINISHED
                        ================================= */

                        clearInterval(
                            countdownTimer
                        );


                        countdownTimer =
                            null;


                        /* =============================
                           HIDE COUNTDOWN
                        ============================= */

                        hideCountdown();


                        /* =============================
                           SHOW DOWNLOAD BUTTON
                        ============================= */

                        secondDownload.style.display =
                            "flex";

                        secondDownload.disabled =
                            false;


                        console.log(
                            "WALAWWA: Download button ready"
                        );

                    },
                    1000
                );
        }
    );


    /* =====================================================
       DOWNLOAD BUTTON CLICK
    ===================================================== */

    secondDownload.addEventListener(
        "click",
        function () {

            console.log(
                "WALAWWA: Download clicked"
            );


            secondDownload.disabled =
                true;


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


/* =========================================================
   START PAGE
========================================================= */

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeDownloadPage
    );

} else {

    initializeDownloadPage();
}
