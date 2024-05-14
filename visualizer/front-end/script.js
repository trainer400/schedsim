var buttonSection = document.querySelector('start');

buttonSection.textContent = "Start";

buttonSection.addEventListener('click', function() {
        function sendMessageToFlask() {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/message', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onload = function () {
                if (xhr.status === 200) {
                    document.getElementById('response').innerHTML = xhr.responseText;
                } else {
                    console.error('Request failed. Status code: ' + xhr.status);
                }
            };
            xhr.send();
        }
});

window.addEventListener('load', function() {
    buttonSection.classList.add("default");
});