// Send command and receive a reply
function cmd(command, response_handler = console.log) {
    if (typeof response_handler !== 'function') {
        response_handler = console.log
    }
    const options = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: '{"cmd": "' + command + '"}',
    };
    const request = new XMLHttpRequest();
    request.open('POST', "api");
    // .setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    request.send(command);
    request.onload = function() {
        if (request.status >= 200 && request.status < 300) {
            response_handler(request.responseText, true)
        } else {
            response_handler("failed \n"+ request.statusText, true);
        }
      };
}

/* Show/hide advanced settings, by toggeling 'advanced" css class */
var advanced = false;
function advanced_toggle_view(checked){
    if( checked !== '') {
        advanced = checked
    } else {
        advanced = !advanced;
    }
    var list_of_elements = document.getElementsByClassName('advanced');
    state = advanced ? 'table-row' : 'none';
    for (let i = 0 ; i < list_of_elements.length; i++){
        list_of_elements[i].style.display = state;
    }
}

/* Select a tab, show corresponding content and hide previous content */
var current_tab_id = "";
function tab_select(name){
    console.log("Selecting tab:",name)
    try{
        if (current_tab_id){
            document.getElementById(current_tab_id).style.display = "none";
        }
    } catch {}
    try{
        document.getElementById(name).style.display = "inline-block";
    } catch {}
    current_tab_id = name;
}

// Terminal
var hist = ['line 1'];
var store = '';
var histIndex = 0;

function consoleInput() {
    var event = window.event || event.which;
    if (event.keyCode == 13) {
        event.preventDefault();
        line = consoleInputElm = document.getElementById("console-input").value;
        consoleOutput(line);
        if (line.length) {
            cmd(line, consoleOutput);
            hist.unshift(line);
            histIndex = 0;
            store = ''
            document.getElementById("console-input").value = "";
        }
        consoleFocus()
    } else if (event.keyCode == 38) { // up
        if (histIndex == 0)
            store = document.getElementById("console-input").value;
        if (histIndex + 2  <= hist.length)
            document.getElementById("console-input").value = hist[histIndex++];
    } else if (event.keyCode == 40) { // Down
        if (histIndex -1 <= 0)
            document.getElementById("console-input").value = store;
        else
            document.getElementById("console-input").value = hist[histIndex--];
    } else if (event.keyCode == 27) { // ESC
        if (histIndex != 0) {
            document.getElementById("console-input").value = store;
            histIndex = 0;
            store = '';
        } else {
            document.getElementById("console-input").value = '';
        }
    }
}

function consoleOutput(text, color = false){
    try {
        let span = document.createElement('span');
        let textNode = document.createTextNode(text);
        span.appendChild(textNode);
        if (color){
            if (text.trim().substr(0,6).toLowerCase() == 'failed'){
                span.classList.add("failed");
            } else {
                span.classList.add("ok");
            }
        }
        document.getElementById("console-output").appendChild(span);
        document.getElementById("console-output").appendChild(document.createElement('BR'));
        // document.getElementById("console").scrollLeft = 0;
    } catch {
    }
    consoleFocus()
}

function consoleFocus(){
    document.getElementById("console-input").focus()
}

function consoleStart(consoleTagID){
    document.addEventListener('DOMContentLoaded', function(){
        // Set the focus to the input so that you can start typing straight away:
        document.getElementById("console-input").value ="";
        consoleFocus();
        // Set focus on input when console become visible
        observer = new MutationObserver(function(){
            if(document.getElementById(consoleTagID).style.display != 'none'){
                consoleFocus();
            }
        });
        observer.observe(document.getElementById(consoleTagID), { attributes: true });
    }, false);

}