
var imageMap = new Map();

// consider socket.on('connect', function(){});


$(document).ready(function(){
    var protocol = window.location.protocol;
    var socket = io.connect(protocol+ '//' + document.domain + ':' + location.port);
    var canvas = document.getElementById("canvas");
    var ctx = canvas.getContext('2d');


    var gameWidth = null;
    var gameHeight = null;

    //to quit any previous sessions
    socket.emit("quit", socket.id);

    mode = window.location.href.split('#')[-1]

    socket.emit('start', "");

    var start = new Date();

   


    socket.on('dimensions', function(msg){
        dims = JSON.parse(msg);
        gameWidth = dims[0];
        gameHeight = dims[1];

        // ctx.fillStyle = "black";
        // ctx.fillRect(10,10,200,100);

    });

    
function drawScaled(x,y,ctx, width = 0,height = 0, image =null , text =null , rectColor = null){


    widthFactor =  canvas.width/gameWidth;
    heightFactor = canvas.height/gameHeight;
    x = x * widthFactor;
    y = y * heightFactor;
    width = width * widthFactor;
    height = height * heightFactor;


    if (image != null){



    ctx.drawImage(image, x, y, width, height);


    } else if (text != null){
        words = text[0]
        font = text[1]
        color = text[2]

        ctx.fillStyle = `rgb(${color[0]},
            ${color[1]},
            ${color[2]})`;

        ctx.font = font;
        ctx.fillText(words,x,y)
        
    } else if (rectColor != null){
        
        ctx.fillStyle = rectColor;

        ctx.fillRect(x,y,width,height)

    }
    }
    var messagesRecieved = 0

    // alert(gameWidth, gameHeight);

    
    function drawQuitButton(rect){

    
        ctx.fillStyle = "red";
    
        ctx.fillRect(rect.x,rect.y, rect.width,rect.height);
        ctx.fillStyle = 'white';
        ctx.font = "20px Verdana";
        ctx.fillText("(M) Menu", rect.x, rect.y + 30, rect.width)
    }
    
    function updateCanvas(objects){

        messagesRecieved += 1
        let secondsElapsed = (new Date() - start)/1000;



        ctx.canvas.width  = window.innerWidth;
        ctx.canvas.height = window.innerHeight;
        console.log(objects)

        objects = JSON.parse(objects);
        for (i = 0; i < objects.length ; i += 1){
            object = objects[i];

            images = object["images"]

            for (j = 0; j < images.length; j++){
                image = images[j];
                // console.log(image)
                let width = image[3];
                let height = image[4];
                let x = image[1];
                let y = image[2];
                let isReversed = image[5];
                let img_path = image[0]
                let src=  "";
                if (isReversed){
                    img_split=  img_path.split("/")
                    imgName = img_split.pop()
                    img_path = img_split.join("/") + "/reverse_"+imgName;
             
                }
                src = "../" + img_path;

                
                // console.log(width)

                if (!imageMap.has(src)){
                    let img = new Image(width, height);
                    img.src = src;
                    
                    img.onload = function(){

                    imageMap.set(src, img);
                    };
                    
                }

                drawScaled(x,y, ctx, width,height,imageMap.get(src))
            }

            texts = object["text"];

            for( j = 0; j<texts.length ; j++){
                text = texts[j];
                
                pos = text[0]
                word = text[1];
                color = text[2];
                font = (0.0250*canvas.height).toString() +"px Arial";
                drawScaled(pos[0], pos[1]+10, ctx, null, null, null, [word, font, color])
            }


            rects = object["rectangles"];

            for( j = 0; j<rects.length ; j++){
                rectangle = rects[j];
                pos = rectangle[0];
                dim = rectangle[1];
                color = rectangle[2]
                

                drawScaled(pos[0], pos[1], ctx, dim[0], dim[1], null,null, color)
            }
            
            ctx.font = "30px Bold Arial";
            ctx.fillStyle = "white";




        }

            
        
        //The rectangle should have x,y,width,height properties
        var rect = {
            x:canvas.width *.45,
            y:canvas.height*.025,
            width:100,
            height:50
        };




        drawQuitButton(rect)
        


    }

    updateCanvas(JSON.stringify([]));


    socket.on('screen', updateCanvas);

    document.addEventListener('keydown', function(event) {
        if(event.key == "a") {
           socket.emit("input", "left");
        }
        else if(event.key == "d") {
            socket.emit("input", "right");
        } else if (event.key == "m"){

            returnToMenu()
        }
    });
    


        //Function to get the mouse position
    function getMousePos(canvas, event) {
        return {
            x: event.clientX,
            y: event.clientY 
        };
    }

    function returnToMenu(){
        console.log("returning to menu")

        socket.emit('quit', socket.id)


        
        setTimeout(window.location.replace("/"));
    }
    //Function to check whether a point is inside a rectangle
    function isInside(pos, rect){
        console.log(pos,rect)
        return pos.x > rect.x && pos.x < rect.x+rect.width && pos.y < rect.y+rect.height && pos.y > rect.y
    }

    //Binding the click event on the canvas
    document.addEventListener('click', function(evt) {
        var mousePos = getMousePos(canvas, evt);

            
        //The rectangle should have x,y,width,height properties
        var rect = {
            x:canvas.width *.45,
            y:canvas.height*.025,
            width:100,
            height:50
        };
        if (isInside(mousePos,rect)) {
            returnToMenu()
        }
    }, false);

});