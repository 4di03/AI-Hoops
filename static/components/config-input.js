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
        <input type = "${this.type}" min = "${this.min}" max = "${this.max}" step = "${this.step}" />
            <span> ${mid}</span>
        </div>`;

        } else if (this.type =="checkbox"){
            this.innerHTML = `${this.text}<div class = "${this.type}" id ="${this.id}">
            <input type = "${this.type}" />
            </div>`;
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

