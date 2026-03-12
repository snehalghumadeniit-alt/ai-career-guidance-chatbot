function sendMessage(){

let msg=document.getElementById("message").value;

if(msg=="") return;

addMessage(msg,"user");

fetch("/chat",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({message:msg})
})
.then(res=>res.json())
.then(data=>{
setTimeout(function(){
addMessage(data.reply,"bot");
},400);
});

document.getElementById("message").value="";
}

function sendQuick(text){

document.getElementById("message").value=text;

sendMessage();

}

function addMessage(text,type){

let chatbox=document.getElementById("chatbox");

let div=document.createElement("div");

div.className=type;

div.innerHTML=text;

chatbox.appendChild(div);

chatbox.scrollTop=chatbox.scrollHeight;
}

function enterKey(e){
if(e.key==="Enter"){
sendMessage();
}
}

function clearChat(){
document.getElementById("chatbox").innerHTML="";
}

function startVoice(){

let recognition=new(window.SpeechRecognition||window.webkitSpeechRecognition)();

recognition.lang="en-IN";

recognition.start();

recognition.onresult=function(event){
document.getElementById("message").value=event.results[0][0].transcript;
};

}
