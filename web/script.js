```javascript
"use strict";


const BOT_USERNAME = "walawwa_downloadBot";

const COUNTDOWN_SECONDS = 5;


let firstDownload = null;

let secondDownload = null;

let countdown = null;

let countdownNumber = null;

let message = null;



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



function makeTelegramLink(code) {

    return (
        "https://t.me/" +
        BOT_USERNAME +
        "?start=" +
        encodeURIComponent(code)
    );

}



function showMessage(
    text,
    type = ""
) {

    if (!message) {

        return;

    }


    message.textContent =
        text;


    message.className =
        "message";


    if (type) {

        message.classList.add(
            type
        );

    }

}



function initializeDownloadPage() {


    console.log(
        "WALAWWA JavaScript loaded"
    );


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


    const code =
        getDownloadCode();


    console.log(
        "Download code:",
        code
    );



    if (
        !firstDownload ||
        !secondDownload ||
        !countdown ||
        !countdownNumber
    ) {

        console.error(
            "WALAWWA: required elements missing"
        );

        return;

    }



    /*
     * INVALID LINK
     */

    if (!code) {

        firstDownload.disabled =
            true;


        firstDownload.innerHTML =
            "<span>Invalid Download Link</span>";


        showMessage(
            "Please open a valid WALAWWA download link.",
            "error"
        );


        return;

    }



    /*
     * INITIAL STATE
     */

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


    /*
     * No old status message.
     */

    showMessage("");



    /*
     * CONTINUE DOWNLOAD
     */

    firstDownload.addEventListener(
        "click",
        function () {


            console.log(
                "Continue Download clicked"
            );


            /*
             * Hide Continue Download
             */

            firstDownload.style.display =
                "none";


            /*
             * Show countdown
             */

            countdown.style.display =
                "flex";


            let remaining =
                COUNTDOWN_SECONDS;


            countdownNumber.textContent =
                remaining;


            /*
             * Keep message empty.
             */

            showMessage("");


            const timer =
                setInterval(
                    function () {


                        remaining--;


                        countdownNumber.textContent =
                            remaining;


                        /*
                         * Countdown finished
                         */

                        if (
                            remaining <= 0
                        ) {


                            clearInterval(
                                timer
                            );


                            /*
                             * Hide countdown
                             */

                            countdown.style.display =
                                "none";


                            /*
                             * Show Download button
                             */

                            secondDownload.style.display =
                                "flex";


                            secondDownload.disabled =
                                false;


                            /*
                             * No "ready" message.
                             */

                            showMessage("");


                        }


                    },
                    1000
                );


        }
    );



    /*
     * DOWNLOAD
     */

    secondDownload.addEventListener(
        "click",
        function () {


            console.log(
                "Download clicked"
            );


            secondDownload.disabled =
                true;


            const telegramLink =
                makeTelegramLink(
                    code
                );


            console.log(
                "Opening Telegram:",
                telegramLink
            );


            window.location.href =
                telegramLink;


        }
    );


}



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
```
