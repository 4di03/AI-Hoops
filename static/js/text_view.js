import { initGame } from './util.js';



var protocol = window.location.protocol;
var socket = io.connect(protocol + '//' + document.domain + ':' + location.port);

$(document).ready(function () {




    // Create a new element
    var newElement = document.createElement("div");

    // Set styles for the element
    newElement.id = "stdout";
    newElement.style.backgroundColor = "black";
    newElement.style.position = "fixed";
    newElement.style.top = "50%";
    newElement.style.left = "50%";
    newElement.style.transform = "translate(-50%, -50%)";
    newElement.style.padding = "20px";
    newElement.style.color = "white";
    newElement.textContent = "TEST TEST TEST";

    // Append the new element to the document body
    document.body.appendChild(newElement);


    function displayStdout(msg) {
        console.log("STDOUT MESSAGE RECIEVED")
        $("#stdout").html(msg);

        //$("#dialog").dialog("open");
    }


    socket.on('connect', function () {

        initGame(socket);

        socket.on('stdout', displayStdout);
    });

});