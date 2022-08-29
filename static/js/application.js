// import {Solo, Train, Winner} from "./modes.js";

function loadGame(){


    document.getElementById("btns").innerHTML = "";

    document.getElementById("content").innerHTML = "<img src='static/assets/ball_loader.gif'></img>";


    

}

function openCanvas(mode, socket){

    // alert(mode.constructor.name)
    // sessionStorage.setItem('mode', JSON.stringify(mode));
    socket.emit("recieve_mode", mode)
    loadGame()

    //waiting for confirmation that mode was recieved
    socket.on("got game", function(msg) {
        setTimeout(
            function(){
                window.location.replace('game');
            }, 1000

        );

    });

}

function openTrainSettings(mode, socket){



    window.location.replace("train")
}




$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var numbers_received = [];

    //receive details from server
    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        //maintain a list of ten numbers
        if (numbers_received.length >= 10){
            numbers_received.shift()
        }            
        numbers_received.push(msg.number);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }
        $('#log').html(numbers_string);

        


        //write other things
    });




    let solo_btn = document.getElementById("solo-btn");
    let train_btn = document.getElementById("train-btn");
    let winner_btn = document.getElementById("winner-btn");
    



    solo_btn.addEventListener('click', event =>{

        
        openCanvas('solo', socket);
    });


    train_btn.addEventListener('click', event =>{

        openTrainSettings('train', socket);
    });


    winner_btn.addEventListener('click', event =>{


        openCanvas('winner', socket);
    });


});