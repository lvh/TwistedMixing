var handlers = {
  "receive": function(data) {
    $(".messages tbody").append(
      $("<tr>")
        .append($("<td>").text(Math.round(new Date() / 1000)))
        .append($("<td>").text(data.sender))
        .append($("<td>").text(data.message))
    );
  }
}

var l = window.location;
var chatSockJSURI = l.protocol + "//" + l.host + "/sockjs";
var sock = new SockJS(chatSockJSURI, {debug: true});
sock.onmessage = function(e) {
  message = JSON.parse(e.data)
  handlers[message.command](message);
};

var name = null;
$("input#name").blur(function() {
  this.disabled = true;
  name = this.value;

  sock.send(JSON.stringify({
    command: "setName",
    name: name
  }));

  newMessage.prop("disabled", false);
  sendMessage.prop("disabled", false);
});

var newMessage = $("input#new-message");
var sendMessage = $("button#send-message");

sendMessage.click(function() {
  if (name === null || newMessage.val() === '') {
    return;
  }

  sock.send(JSON.stringify({
    command: "broadcast",
    message: newMessage.val()
  }));

  newMessage.val('');
});
