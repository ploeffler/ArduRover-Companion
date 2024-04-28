
var ws = new WebSocket('ws://localhost:8080/');
var myTimeout = setInterval(syncfunction, 150);
var minsyncTimeout = setInterval(minsyncfunction,250);
while (ws.CONNECTING) {
  
}
setTimeout(sendinit,100);
ws.onmessage = function(event) {
  msg = JSON.parse(event.data)
  // console.log(msg);

  if (msg.type == "image") {
    var img = document.getElementById(msg.data.creator)
    // console.log(msg.data.creator);
    // var urlObject = URL.createObjectURL(msg.data.image);
    img.src = "data:image/png;base64," + msg.data.image
  }

  if (msg.type == "settingsgroup") {
    var element =  document.getElementById(msg.data);
    console.log(element)
    if (element != null){
      console.log("Settingsgroup already exists")
    } else { 
      var menulist = document.getElementById("topicslist")
      var contenttab = document.getElementById("menucontent")
      var navlink = document.createElement("a")
      navlink.setAttribute("class","nav-link")
      navlink.setAttribute("data-toggle","tab")
      navlink.setAttribute("href",'#'+msg.data)
      navlink.innerHTML = msg.data
      var navitem = document.createElement("li")
      navitem.setAttribute("class","nav-item")
      navitem.innerHTML = navlink.outerHTML
      menulist.appendChild(navitem) 
      var contentdiv = document.createElement("div")
      contentdiv.setAttribute("class","container-fluid tab-pane fade")
      contentdiv.setAttribute("id",msg.data)
      contentdiv.innerHTML="<h2>"+msg.data+"</h2>"
      contenttab.appendChild(contentdiv)
    }

  }
  
  if (msg.type == "settingsitem") {
    var element =  document.getElementById(msg.data.itemname);
    console.log(element)
    if (element != null){
      console.log("Settingsitem already exists")
      element.setAttribute("value",msg.data.value)
    } else { 
      var targettab = document.getElementById(msg.data.itemsection)
      var itemdiv = document.createElement("div")
      itemdiv.setAttribute("class","form-group")
      var itemlabel = document.createElement("label")
      itemlabel.setAttribute("for",msg.data.itemname)
      itemlabel.innerHTML=msg.data.itemname 
      var item = document.createElement("input")
      item.setAttribute("type",msg.data.itemtype)
      item.setAttribute("id",msg.data.itemname)
      item.setAttribute("value",msg.data.value)
      
      itemdiv.append(itemlabel)
      itemdiv.append(item)
      targettab.append(itemdiv)
    }

  }
  if (msg.type=="itemvalue") {
    
  }

}
function sendinit(){
  if (ws.readyState == WebSocket.OPEN) {
    ws.send('{"type":"init"}')
  }// console.log("Data sent")
} 
function syncfunction(){
  if (ws.readyState == WebSocket.OPEN) {
    ws.send('{"type":"sync"}')
  }   

}
function minsyncfunction(){
  if (ws.readyState == WebSocket.OPEN) {
    ws.send('{"type":"minsync"}')
  }   

}
function sendsave(){
  if (ws.readyState == WebSocket.OPEN) {
    ws.send('{"type":"save"}')
  }// console.log("Data sent")
} 

function p1selection(value) {
  let sendstring = '{"type":"cmd","data":{"item":"p1select","value":"'+value+'"}}'
  console.log(sendstring)
  
  ws.send(sendstring)

   
}



function warpsend(item,value) {
  let sendstring = '{"type":"cmd","data":{"item":"'+item+'","value":"'+value+'"}}'
  console.log(sendstring)
  if (ws.readyState == WebSocket.OPEN) {
    ws.send(sendstring)
  }
  
}

function invertsend(element){
  value = "False"
  item = element.id
  if(element.checked) {
    value = "True"
  }
  console.log(item,value)
  let sendstring = '{"type":"cmd","data":{"item":"'+item+'","value":"'+value+'"}}'
  if (ws.readyState == WebSocket.OPEN) {
    ws.send(sendstring)
  }
}