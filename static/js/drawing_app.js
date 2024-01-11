var canvas;
var context;
var clickX = [];
var clickY = [];
var clickDrag = [];
var paint = false;
var curColor = "#ddd";

function drawCanvas() {
    canvas = document.getElementById('canvas');
    context = canvas.getContext("2d");
    context.fillStyle = "#000"; 
    context.fillRect(0, 0, canvas.width, canvas.height);

    canvas.addEventListener('mousedown', function (e) {
        var mouseX = e.pageX - this.offsetLeft;
        var mouseY = e.pageY - this.offsetTop;

        paint = true;
        addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop);
        redraw();
    });

    canvas.addEventListener('mousemove', function (e) {
        if (paint) {
            addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop, true);
            redraw();
        }
    });

    canvas.addEventListener('mouseup', function (e) {
        paint = false;
    });
}

function addClick(x, y, dragging) {
    clickX.push(x);
    clickY.push(y);
    clickDrag.push(dragging);
}

function redraw() {
    context.clearRect(0, 0, context.canvas.width, context.canvas.height);
    context.fillStyle = "#000";
    context.fillRect(0, 0, context.canvas.width, context.canvas.height);
    context.strokeStyle = curColor;
    context.lineJoin = "round";
    context.lineWidth = 3;
    for (var i = 0; i < clickX.length; i++) {
        context.beginPath();
        if (clickDrag[i] && i) {
            context.moveTo(clickX[i - 1], clickY[i - 1]);
        } else {
            context.moveTo(clickX[i] - 1, clickY[i]);
        }
        context.lineTo(clickX[i], clickY[i]);
        context.closePath();
        context.stroke();
    }
}

function predictDigit() {
    var image = new Image();
    var url = document.getElementById('url');
    image.id = "pic";
    image.src = canvas.toDataURL();
    url.value = image.src;

    // AJAX request to Flask route for prediction
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/draw', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var predictionResult = document.getElementById('prediction-result');
            
            // Parse the JSON response
            var response = JSON.parse(xhr.responseText);
            
            // Update the HTML content with the prediction
            predictionResult.innerHTML = 'Predicted Digit: ' + response.predicted_digit;
            
            // Print the prediction to the console for verification
            console.log('Predicted Digit:', response.predicted_digit);
        }
    };
    xhr.send('url=' + encodeURIComponent(url.value));
}

// Initialize drawing canvas
drawCanvas();