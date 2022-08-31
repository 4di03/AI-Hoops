class ConfigInput extends HTMLElement{


    constructor(){
        super();
        this.type = "box";
        this.min = 0;
        this.max = 1000;
        this.step = 1;
        this.text = this.innerHTML;
        this.id = "";
        this.round = "true";        
    }

      
    // component attributes
    static get observedAttributes() {
        return ['type','min','max', 'step', 'id', 'round'];
    }

     
  // attribute change
  attributeChangedCallback(property, oldValue, newValue) {

    if (oldValue === newValue) return;
    this[ property ] = newValue;
    
  }

    
    connectedCallback(){


        var mid = (parseInt(this.max) - parseInt(this.min))/2 + parseInt(this.min);
        if (Number.isInteger(parseFloat(parseFloat(this.step)))){
            mid = Math.round(mid)
        }

        if (this.type == "range"){

        this.innerHTML = `${this.text}<div class = "${this.type}" id ="${this.id}">
        <input  id = ${this.id} type = "${this.type}" min = "${this.min}" max = "${this.max}" step = "${this.step}" />
            <span> ${mid}</span>
        </div>`;

        } else if (this.type =="checkbox"){
            this.innerHTML = `${this.text} <div class = "${this.type}" id ="${this.id}">
            <input id = ${this.id} type = "${this.type}"  checked/>
            </div>`;


        } else if (this.type == "radio"){
            var title = this.text.split(":")[0]
            var options = this.text.split(":")[1].split(",")
            

            let contents = ``;
            for(let i =0; i < options.length; i++){
                let option = options[i];
                
                let checked= "";
                if(i ==0){
                    checked = "checked";
                }

                contents += `<input type ='radio' id ='${option}' value = '${option}' name='${title}' ${checked} /><label for='${option}'>${option}</label><br>`
                
            }

            this.innerHTML =`${title}:<br><div class = '${this.type}' id = '${this.id}'>${contents}</div>`;



        } else if (this.type == "select-dropdown"){
            let split = this.text.split("*")
            var title = split[0]
            var options = split[1].split(",")

            let contents = ``;
            for(let i =0; i < options.length; i++){
                let option = options[i];
                
                contents += `<option value = '${option}'/>${option}</option>`
                
            }

            this.innerHTML =`${title}:<br><div class = '${this.type}' id = '${this.id}'><select  id = ${this.id}>${contents}</select></div>`;



        } else if (this.type == "file"){
            this.innerHTML= `${this.text}<input type="file" id ="${this.id} accept =".txt"></input>`
        }

    }

}

// register component
customElements.define( 'config-input', ConfigInput );


$(function(){

    $('.range input').on('mousemove', function(){
        var getValRange = $(this).val();
        var id = $(this).parent().attr('id');
        var val = ((getValRange/100) * (parseInt(this.max) - parseInt(this.min))) + parseInt(this.min);
        if (Number.isInteger(parseFloat(this.step))){
        var val = Math.round(((getValRange/100) * (parseInt(this.max) - parseInt(this.min))) + parseInt(this.min));
        } 


        $(`#${id} span`).text(val);
    });


    });

