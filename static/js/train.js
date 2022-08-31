// import {openCanvas} from './application.js';

$(document).ready(function(){

    let menu_btn = document.getElementById("menu-btn");
    let submit_btn = document.getElementById("submit-btn");
    

    menu_btn.addEventListener("click", event => {
        window.location.replace("/");
    });

    submit_btn.addEventListener("click", event => {
        // var socket = io.connect('http://' + document.domain + ':' + location.port +"/train");


        //get form data

        var elements = [].slice.call(document.getElementsByTagName("input"));

        elements = elements.concat(document.getElementsByTagName("select"))

        var config ={};
        for(var i = 0 ; i < elements.length ; i++){
            var element = elements[i];
            console.log(element)
            config[element.id] =element.value;
 
        }

        console.log(config)
        

        // console.log(JSON.stringify(config))

        // socket.emit("train_config", JSON.stringify(config));

        // socket.on("confirm_config", function(msg){
        //     openCanvas('train', socket);
        // });
    });

});
