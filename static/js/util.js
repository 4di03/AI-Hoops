export function initGame(socket){
    console.log("emmting quit to " + socket.id)
    //to quit any previous sessions
    socket.emit("quit", socket.id);

    //let mode = window.location.href.split('#')[-1]

    socket.emit('start', socket.id);

    
}

function returnToMenu(socket) {
    console.log("returning to menu")

    socket.emit('quit', socket.id)


    setTimeout(window.location.replace("/"));
}



window.returnToMenu = returnToMenu;

window.initGame = initGame;

$(document).ready(function () {
let menu_btn = document.getElementById("menu-btn"); // add event listener to menu-btn button

if (menu_btn != null){


var protocol = window.location.protocol;
var socket = io.connect(protocol + '//' + document.domain + ':' + location.port);

menu_btn.addEventListener("click", event => {
    window.returnToMenu(socket);
});
}
});