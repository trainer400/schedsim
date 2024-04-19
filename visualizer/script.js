var buttonSection = document.querySelector('.start');

buttonSection.textContent = "Start";

buttonSection.addEventListener('click', function() {
            var name = document.getElementById('nameInput').value;
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/hello', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function () {
                if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    document.getElementById('output').innerText = response.message;
                }
            };
            xhr.send(JSON.stringify({name: name}));
});

window.addEventListener('load', function() {
    buttonSection.classList.add("default");
});