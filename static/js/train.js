// import {Solo, Train, Winner} from "./modes.js";

function loadGame(){


    // document.getElementById("myForm").innerHTML = "";

    document.getElementById("content").innerHTML = "<img src='../static/assets/ball_loader.gif'></img>";

    document.getElementById("content").style.textAlign = "center";
    document.getElementById("content").style.marginTop = "15%";


    

}

function openCanvas(mode, socket){
    socket.emit("recieve_mode", mode)
    loadGame()

    //waiting for confirmation that mode was recieved
    socket.on("got game", function(msg) {

        setTimeout(
            function(){
                window.location.replace('../game');
            }, 1000

        );

    });
}


$(document).ready(function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    let menu_btn = document.getElementById("menu-btn");
    let submit_btn = document.getElementById("submit-btn");
    

    menu_btn.addEventListener("click", event => {
        window.location.replace("/");
    });

    submit_btn.addEventListener("click", event => {


        //get form data

        var elements = [].slice.call(document.getElementsByTagName("input"));

        elements = elements.concat([].slice.call(document.getElementsByTagName("select")))

        var config ={};
        for(var i = 0 ; i < elements.length ; i++){
            var element = elements[i];

            if (element.type == "radio" &&!element.checked){
                    continue;
            }
            let section = $(`config-input#${element.id}`).attr('section')
            config[section] =  config[section] || {};
            config[section][element.id] = element.value;

            //keeps only code customization seettings if config file is already given.
            if (element.id == "config-file" && element.value != ""){
                for(const[key,value] of Object.entries(config)){
                    if(key != "undefined"){
                        delete config['key'];
                    }


                }

                break;
            }
 
        }

        console.log(config)
        

        socket.emit("train_config", JSON.stringify(config));

        socket.on("confirm_config", function(msg){
            openCanvas('train', socket);
        });
    });

});
